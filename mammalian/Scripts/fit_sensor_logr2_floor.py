"""Fit the Main/Supp n=7 mammalian CIC model with a per-sensor log-R2 floor.

The model and shared-parameter hierarchy are unchanged. Optimization starts
from the archived pure-log10 and hybrid solutions, then adaptively increases
the observation weight of any CSV whose log10-scale R2 is below the requested
floor. Among feasible candidates, the solution with the lowest global
unweighted log10(RPU) MSE is selected.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

import model_core as core


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_README = PROJECT_DIR / "README.md"
DEFAULT_INPUT = PROJECT_DIR / "Input"
DEFAULT_OUTPUT = PROJECT_DIR / "Output"
START_FILES = (
    ("pure_log10_archived", "pure_log10_initial_parameter_vector.npy"),
    ("hybrid_raw_log_archived", "hybrid_initial_parameter_vector.npy"),
)

BACKEND = "scipy_sensor_logR2_floor_0p5"
TARGET_R2_LOG10 = 0.5
INTERNAL_TARGET_MARGIN = 5e-4
WEIGHT_GROWTH = 1.35
MAX_REWEIGHT_ROUNDS = 24


def per_csv_log_metrics(
    data: core.FitData,
    layout: core.ParameterLayout,
    vector: np.ndarray,
) -> pd.DataFrame:
    predicted, _ = core.predict_rpu_numpy(data, layout, vector)
    predicted_log = np.log10(np.clip(predicted, 1e-300, None))
    rows: list[dict[str, object]] = []
    for csv_index, mapping in enumerate(data.mappings):
        mask = data.csv_index == csv_index
        observed = data.observed_log10[mask]
        fitted = predicted_log[mask]
        observed_raw = data.observed_rpu[mask]
        fitted_raw = predicted[mask]
        sse = float(np.sum(np.square(fitted - observed)))
        tss = float(np.sum(np.square(observed - np.mean(observed))))
        normalized_sse = sse / tss
        r2 = 1.0 - normalized_sse
        sse_raw = float(np.sum(np.square(fitted_raw - observed_raw)))
        tss_raw = float(np.sum(np.square(observed_raw - np.mean(observed_raw))))
        normalized_sse_raw = sse_raw / tss_raw
        r2_raw = 1.0 - normalized_sse_raw
        rows.append(
            {
                "csv_index": csv_index,
                "csv": mapping.csv_name,
                "sensor_name": mapping.sensor_name,
                "canonical_dbd": mapping.dbd,
                "canonical_lbd": mapping.lbd,
                "n": int(mask.sum()),
                "SSE_log10": sse,
                "TSS_log10": tss,
                "normalized_SSE_log10": normalized_sse,
                "R2_log10": r2,
                "SSE_raw": sse_raw,
                "TSS_raw": tss_raw,
                "normalized_SSE_raw": normalized_sse_raw,
                "R2_raw": r2_raw,
                "target_R2_log10": TARGET_R2_LOG10,
                "passes_R2_log10_floor": bool(r2 >= TARGET_R2_LOG10),
            }
        )
    return pd.DataFrame(rows)


def global_log_mse(
    data: core.FitData,
    layout: core.ParameterLayout,
    vector: np.ndarray,
) -> float:
    predicted, _ = core.predict_rpu_numpy(data, layout, vector)
    return float(
        np.mean(
            np.square(
                np.log10(np.clip(predicted, 1e-300, None)) - data.observed_log10
            )
        )
    )


def fit_one_start(
    label: str,
    initial: np.ndarray,
    data: core.FitData,
    layout: core.ParameterLayout,
    max_nfev: int,
) -> tuple[np.ndarray, pd.DataFrame, list[dict[str, object]], np.ndarray]:
    if max_nfev < 1:
        raise ValueError("max_nfev must be positive")
    layout.decode_numpy(initial)
    core.objective_row_scales(data)  # Reject undefined per-sensor R2 before optimizing.
    lower, upper = layout.bounds()
    vector = np.clip(np.asarray(initial, dtype=float), lower, upper)
    sensor_weights = np.ones(len(data.mappings), dtype=float)
    trace: list[dict[str, object]] = []

    for round_index in range(MAX_REWEIGHT_ROUNDS + 1):
        table = per_csv_log_metrics(data, layout, vector)
        minimum_r2 = float(table["R2_log10"].min())
        mean_r2 = float(table["R2_log10"].mean())
        mse = global_log_mse(data, layout, vector)
        violating = table.loc[
            table["R2_log10"] < TARGET_R2_LOG10 + INTERNAL_TARGET_MARGIN,
            "csv_index",
        ].astype(int).tolist()
        trace.append(
            {
                "start": label,
                "round": round_index,
                "global_MSE_log10": mse,
                "minimum_per_sensor_R2_log10": minimum_r2,
                "mean_per_sensor_R2_log10": mean_r2,
                "violating_sensor_count_at_internal_margin": len(violating),
                "violating_csv": ";".join(
                    table.loc[table["csv_index"].isin(violating), "csv"].tolist()
                ),
                "maximum_sensor_weight": float(sensor_weights.max()),
            }
        )
        print(
            f"[{label}] round={round_index:02d} min_R2_log10={minimum_r2:.8f} "
            f"mean_R2_log10={mean_r2:.8f} log10_MSE={mse:.8g} "
            f"violating={len(violating)}"
        )
        if not violating:
            return vector, table, trace, sensor_weights
        if round_index == MAX_REWEIGHT_ROUNDS:
            break

        for index in violating:
            deficit = max(
                0.0,
                TARGET_R2_LOG10 + INTERNAL_TARGET_MARGIN
                - float(table.loc[table["csv_index"] == index, "R2_log10"].iloc[0]),
            )
            # A slightly larger update for a larger deficit, while preserving
            # the pure-log solution when only a small correction is required.
            sensor_weights[index] *= WEIGHT_GROWTH ** (1.0 + 4.0 * deficit)

        row_scale = np.sqrt(sensor_weights[data.csv_index])

        def residuals(parameters: np.ndarray) -> np.ndarray:
            predicted, _ = core.predict_rpu_numpy(data, layout, parameters)
            log_residual = (
                np.log10(np.clip(predicted, 1e-300, None)) - data.observed_log10
            )
            return log_residual * row_scale

        fit = least_squares(
            residuals,
            vector,
            bounds=(lower, upper),
            method="trf",
            max_nfev=max_nfev,
            ftol=1e-12,
            xtol=1e-12,
            gtol=1e-12,
            x_scale="jac",
        )
        vector = fit.x

    return vector, per_csv_log_metrics(data, layout, vector), trace, sensor_weights


def choose_candidate(candidates: list[dict[str, object]]) -> dict[str, object]:
    if not candidates:
        raise ValueError("No fit candidates were provided")
    if any(not np.isfinite(float(candidate[key])) for candidate in candidates
           for key in ("global_MSE_log10", "minimum_R2_log10", "mean_R2_log10")):
        raise ValueError("Fit candidate metrics must be finite")
    feasible = [candidate for candidate in candidates if bool(candidate["feasible"])]
    if feasible:
        return min(feasible, key=lambda candidate: float(candidate["global_MSE_log10"]))
    return max(
        candidates,
        key=lambda candidate: (
            float(candidate["minimum_R2_log10"]),
            float(candidate["mean_R2_log10"]),
            -float(candidate["global_MSE_log10"]),
        ),
    )


def write_outputs(
    selected: dict[str, object],
    candidates: list[dict[str, object]],
    trace_rows: list[dict[str, object]],
    data: core.FitData,
    layout: core.ParameterLayout,
    output_root: Path,
    elapsed: float,
) -> Path:
    vector = np.asarray(selected["vector"], dtype=float)
    metrics = per_csv_log_metrics(data, layout, vector)
    weights = np.asarray(selected["sensor_weights"], dtype=float)
    metrics["final_observation_weight_multiplier"] = weights[
        metrics["csv_index"].to_numpy(int)
    ]

    result = core.FitResult(
        backend=BACKEND,
        parameter_vector=vector,
        objective_total=float(selected["global_MSE_log10"]),
        elapsed_seconds=elapsed,
        status="success" if bool(selected["feasible"]) else "best_infeasible",
        message=(
            "All 25 sensors satisfy log10-scale R2 >= 0.5"
            if bool(selected["feasible"])
            else "No feasible solution found; saved best minimum-R2 candidate"
        ),
        diagnostics={
            "selected_start": selected["label"],
            "target_R2_log10": TARGET_R2_LOG10,
            "internal_target_margin": INTERNAL_TARGET_MARGIN,
            "reweight_growth": WEIGHT_GROWTH,
            "maximum_reweight_rounds": MAX_REWEIGHT_ROUNDS,
        },
    )
    core.write_result(result, data, layout, output_root)
    backend_dir = output_root / BACKEND

    metrics.to_csv(backend_dir / "constraint_metrics.csv", index=False)
    pd.DataFrame(trace_rows).to_csv(backend_dir / "optimization_trace.csv", index=False)
    candidate_rows = []
    for candidate in candidates:
        candidate_rows.append(
            {
                "start": candidate["label"],
                "feasible": candidate["feasible"],
                "minimum_R2_log10": candidate["minimum_R2_log10"],
                "mean_R2_log10": candidate["mean_R2_log10"],
                "global_MSE_log10": candidate["global_MSE_log10"],
                "selected": candidate is selected,
            }
        )
    pd.DataFrame(candidate_rows).to_csv(
        backend_dir / "candidate_comparison.csv", index=False
    )

    parameter_lbd = pd.read_csv(backend_dir / "parameters_lbd.csv")
    parameter_lbd["weak_shape_prior_applied"] = False
    parameter_lbd.to_csv(backend_dir / "parameters_lbd.csv", index=False)

    objective = {
        "global_unweighted_MSE_log10": float(selected["global_MSE_log10"]),
        "minimum_per_sensor_R2_log10": float(metrics["R2_log10"].min()),
        "mean_per_sensor_R2_log10": float(metrics["R2_log10"].mean()),
        "target_R2_log10": TARGET_R2_LOG10,
        "passing_sensor_count": int(metrics["passes_R2_log10_floor"].sum()),
        "included_sensor_count": len(metrics),
        "constraint_satisfied": bool(metrics["passes_R2_log10_floor"].all()),
    }
    pd.DataFrame([objective]).to_csv(
        backend_dir / "objective_components.csv", index=False
    )

    summary = {
        "backend": BACKEND,
        "status": result.status,
        "message": result.message,
        "objective": (
            "lexicographic: require every included CSV log10-scale R2 >= 0.5; "
            "among feasible adaptive-reweighted candidates select the lowest "
            "global unweighted mean squared error in log10(RPU)"
        ),
        "constraint": objective,
        "selected_start": selected["label"],
        "elapsed_seconds": elapsed,
        "Tmax": core.TMAX,
        "operator_number": core.OPERATOR_NUMBER,
        "anchor_DBD": core.ANCHOR_DBD,
        "anchor_KA": core.ANCHOR_KA,
        "included_CSV_count": len(data.mappings),
        "excluded_CSV": sorted(core.EXCLUDED_CSV),
        "LBD_parameter_groups": len(layout.lbd_names),
        "DBD_parameter_groups": len(layout.dbd_names),
        "free_parameter_count": layout.size,
        "parameter_hierarchy": {
            "same_LBD_shares": ["Kd0", "Kb", "Kd1"],
            "same_DBD_shares": ["KA", "T0_variant"],
        },
        "shape_prior": {
            "weight": 0.0,
            "reason": "disabled so the explicit per-sensor R2 floor is the governing constraint",
        },
        "diagnostics": result.diagnostics,
    }
    (backend_dir / "fit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return backend_dir


def load_start_vectors(input_dir: Path, layout: core.ParameterLayout):
    """Resolve both archived vectors against the requested input directory."""
    missing = [str(input_dir / filename) for _, filename in START_FILES
               if not (input_dir / filename).is_file()]
    if missing:
        raise FileNotFoundError("Missing archived initial parameters: " + ", ".join(missing))
    starts = []
    for label, filename in START_FILES:
        vector = np.load(input_dir / filename, allow_pickle=False)
        layout.decode_numpy(vector)
        starts.append((label, vector))
    return starts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-nfev", type=int, default=50_000)
    parser.add_argument("--list-mappings", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    mappings = core.read_sensor_mapping(args.readme.resolve())
    core.print_mapping_summary(mappings)
    if args.list_mappings:
        return
    data = core.load_fit_data(args.input_dir.resolve(), mappings)
    layout = core.ParameterLayout(data.mappings)
    starts = load_start_vectors(args.input_dir.resolve(), layout)
    candidates: list[dict[str, object]] = []
    all_trace: list[dict[str, object]] = []
    started = time.perf_counter()
    for label, initial in starts:
        vector, table, trace, weights = fit_one_start(
            label, initial, data, layout, args.max_nfev
        )
        all_trace.extend(trace)
        candidates.append(
            {
                "label": label,
                "vector": vector,
                "sensor_weights": weights,
                "feasible": bool((table["R2_log10"] >= TARGET_R2_LOG10).all()),
                "minimum_R2_log10": float(table["R2_log10"].min()),
                "mean_R2_log10": float(table["R2_log10"].mean()),
                "global_MSE_log10": global_log_mse(data, layout, vector),
            }
        )
    selected = choose_candidate(candidates)
    elapsed = time.perf_counter() - started
    backend_dir = write_outputs(
        selected,
        candidates,
        all_trace,
        data,
        layout,
        args.output_dir.resolve(),
        elapsed,
    )
    print(
        json.dumps(
            {
                "output": str(backend_dir),
                "selected_start": selected["label"],
                "constraint_satisfied": selected["feasible"],
                "minimum_R2_log10": selected["minimum_R2_log10"],
                "global_MSE_log10": selected["global_MSE_log10"],
                "elapsed_seconds": elapsed,
            },
            indent=2,
        )
    )
    if not selected["feasible"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
