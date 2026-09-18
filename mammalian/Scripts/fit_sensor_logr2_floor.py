"""Fit the Main/Supp n=7 mammalian CIC model with a per-sensor log-R2 floor.

The model and shared-parameter hierarchy are unchanged. Each archived start
first minimizes macro mean per-CSV (1 - R2_log10). Adaptive CSV weights then
seek the explicit R2_log10 >= 0.5 constraint. Log residuals are normalized by
each CSV's log10 SST and the CSV count. Among feasible candidates, the largest
macro mean per-CSV R2_log10 is selected. Raw R2 and global log MSE are diagnostics.
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
    core.objective_row_scales(data)
    predicted, _ = core.predict_rpu_numpy(data, layout, vector)
    predicted_log = core.log10_positive(predicted, "Predicted RPU")
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
                core.log10_positive(predicted, "Predicted RPU") - data.observed_log10
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
    log_scales = core.objective_row_scales(data)
    lower, upper = layout.bounds()
    vector = np.clip(np.asarray(initial, dtype=float), lower, upper)
    sensor_weights = np.ones(len(data.mappings), dtype=float)
    trace: list[dict[str, object]] = []
    evaluated = []

    for round_index in range(MAX_REWEIGHT_ROUNDS + 1):
        table = per_csv_log_metrics(data, layout, vector)
        minimum_r2 = float(table["R2_log10"].min())
        mean_r2 = float(table["R2_log10"].mean())
        mse = global_log_mse(data, layout, vector)
        evaluated.append({
            "vector": vector.copy(), "table": table,
            "sensor_weights": sensor_weights.copy(),
            "feasible": bool(minimum_r2 >= TARGET_R2_LOG10),
            "minimum_R2_log10": minimum_r2, "mean_R2_log10": mean_r2,
            "global_MSE_log10": mse,
        })
        violating = table.loc[
            table["R2_log10"] < TARGET_R2_LOG10 + INTERNAL_TARGET_MARGIN,
            "csv_index",
        ].astype(int).tolist()
        trace.append(
            {
                "start": label,
                "round": round_index,
                "global_MSE_log10": mse,
                "objective_total": float(table["normalized_SSE_log10"].mean()),
                "weighted_search_objective": float(np.mean(sensor_weights * table["normalized_SSE_log10"])),
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
        if not violating and round_index > 0:
            break
        if round_index == MAX_REWEIGHT_ROUNDS:
            break

        # The first fit always uses the pure macro-log10-R2 objective, even
        # when the archived initial vector already satisfies the constraint.
        for index in (violating if round_index > 0 else []):
            deficit = max(
                0.0,
                TARGET_R2_LOG10 + INTERNAL_TARGET_MARGIN
                - float(table.loc[table["csv_index"] == index, "R2_log10"].iloc[0]),
            )
            # A slightly larger update for a larger deficit, while preserving
            # the pure-log solution when only a small correction is required.
            sensor_weights[index] *= WEIGHT_GROWTH ** (1.0 + 4.0 * deficit)

        row_scale = log_scales * np.sqrt(sensor_weights[data.csv_index])

        def residuals(parameters: np.ndarray) -> np.ndarray:
            predicted, _ = core.predict_rpu_numpy(data, layout, parameters)
            log_residual = (
                core.log10_positive(predicted, "Predicted RPU") - data.observed_log10
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

    selected = choose_candidate(evaluated)
    return selected["vector"], selected["table"], trace, selected["sensor_weights"]


def choose_candidate(candidates: list[dict[str, object]]) -> dict[str, object]:
    if not candidates:
        raise ValueError("No fit candidates were provided")
    if any(not np.isfinite(float(candidate[key])) for candidate in candidates
           for key in ("global_MSE_log10", "minimum_R2_log10", "mean_R2_log10")):
        raise ValueError("Fit candidate metrics must be finite")
    if any(bool(candidate["feasible"]) != (float(candidate["minimum_R2_log10"]) >= TARGET_R2_LOG10)
           for candidate in candidates):
        raise ValueError("Fit candidate feasibility disagrees with the per-sensor R2 floor")
    feasible = [candidate for candidate in candidates if bool(candidate["feasible"])]
    if feasible:
        return max(feasible, key=lambda candidate: (float(candidate["mean_R2_log10"]),
                                                     float(candidate["minimum_R2_log10"])))
    return max(
        candidates,
        key=lambda candidate: (
            float(candidate["minimum_R2_log10"]),
            float(candidate["mean_R2_log10"]),
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
    # Recompute the candidate claims from their vectors before creating files.
    # A caller cannot promote an infeasible vector by changing a metadata flag.
    if not any(candidate is selected for candidate in candidates):
        raise ValueError("Selected candidate is absent from the candidate list")
    for candidate in candidates:
        checked = per_csv_log_metrics(data, layout, np.asarray(candidate["vector"], dtype=float))
        expected = {"minimum_R2_log10": float(checked["R2_log10"].min()),
                    "mean_R2_log10": float(checked["R2_log10"].mean()),
                    "global_MSE_log10": global_log_mse(data, layout, candidate["vector"])}
        if (bool(candidate["feasible"]) != bool(checked["passes_R2_log10_floor"].all())
                or any(not np.isclose(float(candidate[key]), value, rtol=1e-10, atol=1e-12)
                       for key, value in expected.items())):
            raise ValueError("Fit candidate metadata disagrees with recomputed objective or constraints")
    if choose_candidate(candidates) is not selected:
        raise ValueError("Selected candidate does not maximize feasible macro log10 R2")
    vector = np.asarray(selected["vector"], dtype=float)
    metrics = per_csv_log_metrics(data, layout, vector)
    weights = np.asarray(selected["sensor_weights"], dtype=float)
    if weights.shape != (len(data.mappings),) or not np.isfinite(weights).all() or np.any(weights <= 0):
        raise ValueError("Fit candidate sensor weights must be finite and positive")
    metrics["final_observation_weight_multiplier"] = weights[
        metrics["csv_index"].to_numpy(int)
    ]

    result = core.FitResult(
        backend=BACKEND,
        parameter_vector=vector,
        objective_total=float(metrics["normalized_SSE_log10"].mean()),
        elapsed_seconds=elapsed,
        status="success" if bool(selected["feasible"]) else "best_infeasible",
        message=(
            "All included sensors satisfy log10-scale R2 >= 0.5"
            if bool(selected["feasible"])
            else "No feasible solution found; saved best minimum-R2 candidate"
        ),
        diagnostics={
            "selected_start": selected["label"],
            "target_R2_log10": TARGET_R2_LOG10,
            "internal_target_margin": INTERNAL_TARGET_MARGIN,
            "reweight_growth": WEIGHT_GROWTH,
            "maximum_reweight_rounds": MAX_REWEIGHT_ROUNDS,
            "search_objective": "macro mean sensor_weight * (1 - R2_log10); adaptive feasibility search",
            "selection_objective": "maximum unweighted macro mean per-CSV R2_log10 among feasible candidates",
        },
    )
    summary = core.write_result(result, data, layout, output_root)
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
                "objective_total": 1.0 - float(candidate["mean_R2_log10"]),
                "global_MSE_log10": candidate["global_MSE_log10"],
                "selected": candidate is selected,
            }
        )
    pd.DataFrame(candidate_rows).to_csv(
        backend_dir / "candidate_comparison.csv", index=False
    )

    constraint = {
        "global_unweighted_MSE_log10": float(selected["global_MSE_log10"]),
        "minimum_per_sensor_R2_log10": float(metrics["R2_log10"].min()),
        "mean_per_sensor_R2_log10": float(metrics["R2_log10"].mean()),
        "target_R2_log10": TARGET_R2_LOG10,
        "passing_sensor_count": int(metrics["passes_R2_log10_floor"].sum()),
        "included_sensor_count": len(metrics),
        "constraint_satisfied": bool(metrics["passes_R2_log10_floor"].all()),
    }
    objective = {**summary["objective_components"], **constraint}
    pd.DataFrame([objective]).to_csv(
        backend_dir / "objective_components.csv", index=False
    )

    summary.update({
        "objective_components": objective,
        "constraint": constraint,
        "selection_rule": (
            "require every included CSV R2_log10 >= 0.5; maximize macro mean "
            "per-CSV R2_log10 among feasible candidates; if none is feasible, "
            "save the largest minimum per-CSV R2_log10 for diagnostics and exit 2"
        ),
        "selected_start": selected["label"],
        "parameter_hierarchy": {
            "same_LBD_shares": ["Kd0", "Kb", "Kd1"],
            "same_DBD_shares": ["KA", "T0_variant"],
        },
    })
    (backend_dir / "fit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=float) + "\n", encoding="utf-8"
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
                "mean_R2_log10": selected["mean_R2_log10"],
                "objective_total": 1.0 - float(selected["mean_R2_log10"]),
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
