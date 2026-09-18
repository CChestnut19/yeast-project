"""Manuscript-aligned mammalian CIC dose-response fitting.

Both fitting backends use the same deterministic model and parameter hierarchy:

* LBD-specific shared parameters: Kd0, Kb, Kd1.
* DBD-specific shared parameters: KA, T0_variant.
* KA_lexAec87 is fixed to 9.15.
* Tmax is fixed to 13.61 RPU.
* Seven independent operator sites are represented by
  p7 = 1 - (1 - p1)**7.
* Both SciPy curve_fit and PyTorch/Adam minimize the same log10 objective:
  macro mean per-CSV (1 - R2_log10).
  Every CSV contributes equally.
* Raw-scale R2 is diagnostic only. No shape prior enters the objective.

CSV/sensor/DBD/LBD mappings are parsed from the project README. 402.csv is
retained as an input control but excluded from CIC fitting.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DEFAULT_README = PROJECT_DIR / "README.md"
DEFAULT_INPUT_DIR = PROJECT_DIR / "Input"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "Output"

TMAX = 13.61
OPERATOR_NUMBER = 7
ANCHOR_DBD = "lexAec87"
ANCHOR_KA = 9.15
EXCLUDED_CSV = {"402.csv"}
REQUIRED_COLUMNS = ("LBD", "inducer", "RPU")
OBJECTIVE_DESCRIPTION = "macro mean per-CSV (1 - R2_log10)"
CURVE_GRID_POINTS = 400
ZERO_ENDPOINT_GRID_DECADES = 6.0
SCIPY_BACKEND = "scipy_curve_fit_macro_log10_r2"
TORCH_BACKEND = "pytorch_adam_macro_log10_r2"


@dataclass(frozen=True)
class SensorMapping:
    csv_name: str
    sensor_name: str
    source_dbd: str
    dbd: str
    lbd: str
    included: bool


@dataclass
class FitData:
    frame: pd.DataFrame
    mappings: list[SensorMapping]
    ctf_all: np.ndarray
    inducer: np.ndarray
    observed_rpu: np.ndarray
    observed_log10: np.ndarray
    lbd_index: np.ndarray
    dbd_index: np.ndarray
    csv_index: np.ndarray


@dataclass
class DecodedParameters:
    Kd0: np.ndarray
    Kb: np.ndarray
    Kd1: np.ndarray
    KA: np.ndarray
    T0_variant: np.ndarray


@dataclass
class FitResult:
    backend: str
    parameter_vector: np.ndarray
    objective_total: float
    elapsed_seconds: float
    status: str
    message: str
    diagnostics: dict[str, object]


def strip_markdown(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        value = value[1:-1]
    return value.strip()


def read_sensor_mapping(readme_path: Path) -> list[SensorMapping]:
    """Read the six-column CSV mapping table from README.md."""

    if not readme_path.is_file():
        raise FileNotFoundError(f"README mapping file not found: {readme_path}")

    mappings: list[SensorMapping] = []
    seen: set[str] = set()
    for raw_line in readme_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.lstrip().startswith("|"):
            continue
        cells = [strip_markdown(cell) for cell in raw_line.strip().strip("|").split("|")]
        if not cells or not re.fullmatch(r"\d+\.csv", cells[0]):
            continue
        if len(cells) < 6:
            raise ValueError(
                "README mapping rows must contain six columns: CSV, Sensor name, "
                "Source DBD, Canonical DBD, Canonical LBD, Fit status. "
                f"Invalid row: {raw_line}"
            )
        csv_name, sensor_name, source_dbd, dbd, lbd, fit_status = cells[:6]
        if csv_name in seen:
            raise ValueError(f"Duplicate CSV mapping in README: {csv_name}")
        seen.add(csv_name)
        included = fit_status.casefold() == "included"
        mappings.append(
            SensorMapping(
                csv_name=csv_name,
                sensor_name=sensor_name,
                source_dbd=source_dbd,
                dbd=dbd,
                lbd=lbd,
                included=included,
            )
        )

    if not mappings:
        raise ValueError(f"No CSV mapping rows found in {readme_path}")
    if {m.csv_name for m in mappings if not m.included} != EXCLUDED_CSV:
        raise ValueError(
            "README exclusion set does not match the confirmed workflow. "
            f"Expected {sorted(EXCLUDED_CSV)}; found "
            f"{sorted(m.csv_name for m in mappings if not m.included)}"
        )
    return mappings


def load_fit_data(input_dir: Path, mappings: Sequence[SensorMapping]) -> FitData:
    """Load all included CIC CSVs and assign stable mapping-based indices."""

    included = [mapping for mapping in mappings if mapping.included]
    if len(included) != 25:
        raise ValueError(f"Expected 25 included CIC CSVs; found {len(included)}")

    lbd_order = list(dict.fromkeys(mapping.lbd for mapping in included))
    dbd_order = list(dict.fromkeys(mapping.dbd for mapping in included))
    lbd_lookup = {name: index for index, name in enumerate(lbd_order)}
    dbd_lookup = {name: index for index, name in enumerate(dbd_order)}

    frames: list[pd.DataFrame] = []
    for csv_index, mapping in enumerate(included):
        csv_path = input_dir / mapping.csv_name
        if not csv_path.is_file():
            raise FileNotFoundError(f"Mapped CSV is missing: {csv_path}")
        frame = pd.read_csv(csv_path)
        missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
        if missing:
            raise ValueError(f"{mapping.csv_name} is missing columns: {missing}")
        # Ignore entirely blank records, but never silently discard a partial observation.
        frame = frame.dropna(subset=list(REQUIRED_COLUMNS), how="all").copy()
        if frame.empty:
            raise ValueError(f"{mapping.csv_name} contains no observations")
        for column in REQUIRED_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="raise")
        if not np.isfinite(frame[list(REQUIRED_COLUMNS)].to_numpy(float)).all():
            raise ValueError(f"{mapping.csv_name} contains missing or non-finite observations")
        if (frame[["LBD", "inducer"]] < 0).any().any():
            raise ValueError(f"{mapping.csv_name} concentrations must be non-negative")
        if (frame["RPU"] <= 0).any():
            bad_rows = frame.index[frame["RPU"] <= 0].tolist()
            raise ValueError(
                f"{mapping.csv_name} contains non-positive RPU at rows {bad_rows}; "
                "log10 fitting requires RPU > 0."
            )
        if frame["RPU"].nunique() < 2:
            raise ValueError(f"{mapping.csv_name} has zero variance; per-sensor R2 is undefined")
        frame.insert(0, "source_row", frame.index + 2)
        frame.insert(0, "csv_index", csv_index)
        frame.insert(0, "lbd_index", lbd_lookup[mapping.lbd])
        frame.insert(0, "dbd_index", dbd_lookup[mapping.dbd])
        frame.insert(0, "canonical_lbd", mapping.lbd)
        frame.insert(0, "canonical_dbd", mapping.dbd)
        frame.insert(0, "source_dbd", mapping.source_dbd)
        frame.insert(0, "sensor_name", mapping.sensor_name)
        frame.insert(0, "csv", mapping.csv_name)
        frames.append(frame)

    combined = pd.concat(frames, ignore_index=True)
    data = FitData(
        frame=combined,
        mappings=included,
        ctf_all=combined["LBD"].to_numpy(dtype=float),
        inducer=combined["inducer"].to_numpy(dtype=float),
        observed_rpu=combined["RPU"].to_numpy(dtype=float),
        observed_log10=np.log10(combined["RPU"].to_numpy(dtype=float)),
        lbd_index=combined["lbd_index"].to_numpy(dtype=int),
        dbd_index=combined["dbd_index"].to_numpy(dtype=int),
        csv_index=combined["csv_index"].to_numpy(dtype=int),
    )
    objective_row_scales(data)
    return data


class ParameterLayout:
    """Stable flat-vector layout shared by SciPy and PyTorch."""

    def __init__(self, mappings: Sequence[SensorMapping]):
        self.lbd_names = list(dict.fromkeys(mapping.lbd for mapping in mappings))
        self.dbd_names = list(dict.fromkeys(mapping.dbd for mapping in mappings))
        if ANCHOR_DBD not in self.dbd_names:
            raise ValueError(f"Anchor DBD {ANCHOR_DBD!r} is absent from included mappings")
        self.free_ka_dbd_names = [name for name in self.dbd_names if name != ANCHOR_DBD]

        cursor = 0
        self.log_Kd0 = slice(cursor, cursor + len(self.lbd_names))
        cursor = self.log_Kd0.stop
        self.log_Kb = slice(cursor, cursor + len(self.lbd_names))
        cursor = self.log_Kb.stop
        self.log_Kd1 = slice(cursor, cursor + len(self.lbd_names))
        cursor = self.log_Kd1.stop
        self.log_KA_free = slice(cursor, cursor + len(self.free_ka_dbd_names))
        cursor = self.log_KA_free.stop
        self.T0_variant = slice(cursor, cursor + len(self.dbd_names))
        cursor = self.T0_variant.stop
        self.size = cursor

        self.lbd_lookup = {name: index for index, name in enumerate(self.lbd_names)}
        self.dbd_lookup = {name: index for index, name in enumerate(self.dbd_names)}

    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        lower = np.full(self.size, -16.0, dtype=float)
        upper = np.full(self.size, 12.0, dtype=float)
        # KA values are apparent positive weights; this range is deliberately broad.
        lower[self.log_KA_free] = -8.0
        upper[self.log_KA_free] = 8.0
        lower[self.T0_variant] = 1e-8
        upper[self.T0_variant] = TMAX - 1e-8
        return lower, upper

    def initial_vector(self, data: FitData, variant: int = 0) -> np.ndarray:
        vector = np.zeros(self.size, dtype=float)

        # Stable, scale-aware starting values. Variants provide deterministic
        # alternatives analogous to the legacy script's fallback guesses.
        kd0_starts = (1e-4, 1e-6, 1e-3)
        kd1_starts = (1.0, 1e4, 1e2)
        kb_multipliers = (1.0, 10.0, 0.1)
        variant_index = variant % len(kd0_starts)
        vector[self.log_Kd0] = math.log10(kd0_starts[variant_index])
        vector[self.log_Kd1] = math.log10(kd1_starts[variant_index])

        for lbd_index, _ in enumerate(self.lbd_names):
            mask = data.lbd_index == lbd_index
            positive_inducer = data.inducer[mask & (data.inducer > 0)]
            scale = float(np.median(positive_inducer)) if positive_inducer.size else 1.0
            kb_start = kb_multipliers[variant_index] / max(scale, 1e-12)
            vector[self.log_Kb.start + lbd_index] = np.clip(math.log10(kb_start), -12, 8)

        vector[self.log_KA_free] = 0.0
        for dbd_index, _ in enumerate(self.dbd_names):
            mask = data.dbd_index == dbd_index
            # A low quantile is more stable than a single minimum replicate.
            t0_start = float(np.quantile(data.observed_rpu[mask], 0.05))
            vector[self.T0_variant.start + dbd_index] = np.clip(
                t0_start, 1e-5, TMAX * 0.5
            )
        return vector

    def decode_numpy(self, vector: np.ndarray) -> DecodedParameters:
        vector = np.asarray(vector, dtype=float)
        if vector.shape != (self.size,):
            raise ValueError(f"Expected parameter vector length {self.size}; got {vector.shape}")
        if not np.isfinite(vector).all():
            raise ValueError("Parameter vector must contain only finite values")
        ka_values: dict[str, float] = {ANCHOR_DBD: ANCHOR_KA}
        free_values = np.power(10.0, vector[self.log_KA_free])
        ka_values.update(dict(zip(self.free_ka_dbd_names, free_values)))
        return DecodedParameters(
            Kd0=np.power(10.0, vector[self.log_Kd0]),
            Kb=np.power(10.0, vector[self.log_Kb]),
            Kd1=np.power(10.0, vector[self.log_Kd1]),
            KA=np.asarray([ka_values[name] for name in self.dbd_names], dtype=float),
            T0_variant=vector[self.T0_variant].copy(),
        )


def predict_rpu_numpy(
    data: FitData,
    layout: ParameterLayout,
    vector: np.ndarray,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Evaluate the manuscript-aligned seven-operator CIC output model."""

    parameters = layout.decode_numpy(vector)
    Kd0 = parameters.Kd0[data.lbd_index]
    Kb = parameters.Kb[data.lbd_index]
    Kd1 = parameters.Kd1[data.lbd_index]
    KA = parameters.KA[data.dbd_index]
    T0_variant = parameters.T0_variant[data.dbd_index]

    return cic_response_numpy(
        data.inducer, data.ctf_all, Kd0, Kb, Kd1, KA, T0_variant
    )


def cic_response_numpy(inducer, ctf_all, Kd0, Kb, Kd1, KA, T0_variant, tmax=TMAX):
    """Shared n=7 response for fitting and numerical analysis (scalars or broadcastable arrays)."""
    inducer = np.asarray(inducer, dtype=float)
    ctf_all = np.asarray(ctf_all, dtype=float)
    B = 1.0 + Kb * inducer
    D = Kd0 + (Kb**2) * Kd1 * (inducer**2)
    S = np.sqrt(B**2 + 8.0 * ctf_all * D)

    # Rationalized mass balance avoids catastrophic cancellation when S is near B.
    ctf_eff = D * np.square(2.0 * ctf_all / (S + B))
    Z = KA * ctf_eff
    p1 = Z / (1.0 + Z)
    p7 = -np.expm1(-OPERATOR_NUMBER * np.log1p(Z))
    predicted = T0_variant + (tmax - T0_variant) * p7

    return predicted, {
        "B": B,
        "D": D,
        "S": S,
        "cTF_eff": ctf_eff,
        "Z": Z,
        "p1": p1,
        "p7": p7,
    }


def endpoint_only_lbd_indices(data: FitData, layout: ParameterLayout) -> np.ndarray:
    """Return LBD indices having no CSV with more than two inducer levels."""

    full_curve_lbd_names: set[str] = set()
    for csv_index, mapping in enumerate(data.mappings):
        inducer_count = np.unique(data.inducer[data.csv_index == csv_index]).size
        if inducer_count > 2:
            full_curve_lbd_names.add(mapping.lbd)
    return np.asarray(
        [
            index
            for index, name in enumerate(layout.lbd_names)
            if name not in full_curve_lbd_names
        ],
        dtype=int,
    )


def log10_positive(values: np.ndarray, name: str = "RPU") -> np.ndarray:
    """Reject invalid log-scale values instead of clipping them into observations."""
    values = np.asarray(values, dtype=float)
    if values.size == 0 or not np.isfinite(values).all() or np.any(values <= 0):
        raise ValueError(f"{name} must be nonempty, finite and strictly positive")
    return np.log10(values)


def objective_row_scales(data: FitData) -> np.ndarray:
    """Return 1/sqrt(CSV_count * SST_log10) per row for equal-CSV R2 loss."""

    csv_count = len(data.mappings)
    observed_log10 = log10_positive(data.observed_rpu, "Observed RPU")
    if csv_count == 0 or not np.array_equal(data.observed_log10, observed_log10):
        raise ValueError("Observed log10 RPU must match positive input observations")
    if data.csv_index.shape != observed_log10.shape or set(data.csv_index) != set(range(csv_count)):
        raise ValueError("CSV indices must cover exactly the mapped observation groups")
    log_scales = np.empty_like(observed_log10)
    for csv_index in range(csv_count):
        mask = data.csv_index == csv_index
        observed_log = data.observed_log10[mask]
        tss_log = float(np.sum(np.square(observed_log - np.mean(observed_log))))
        if np.all(observed_log == observed_log[0]) or not np.isfinite(tss_log) or tss_log <= 0.0:
            raise ValueError(
                f"CSV {data.mappings[csv_index].csv_name} has zero variance and "
                "cannot contribute a per-CSV R2 objective."
            )
        log_scales[mask] = 1.0 / math.sqrt(csv_count * tss_log)
    return log_scales


def objective_components_numpy(
    data: FitData,
    layout: ParameterLayout,
    vector: np.ndarray,
    log_scales: np.ndarray | None = None,
) -> dict[str, float]:
    if log_scales is None:
        log_scales = objective_row_scales(data)
    predicted, _ = predict_rpu_numpy(data, layout, vector)
    predicted_log = log10_positive(predicted, "Predicted RPU")
    log_loss = float(
        np.sum(np.square((predicted_log - data.observed_log10) * log_scales))
    )
    raw_r2 = [r_squared(data.observed_rpu[data.csv_index == index], predicted[data.csv_index == index])
              for index in range(len(data.mappings))]
    return {
        "macro_log10_1_minus_R2": log_loss,
        "data_objective": log_loss,
        "objective_total": log_loss,
        "macro_R2_raw": float(np.mean(raw_r2)),
        "macro_R2_log10": 1.0 - log_loss,
    }


def fit_scipy(
    data: FitData,
    layout: ParameterLayout,
    max_nfev: int,
    starts: int,
) -> FitResult:
    """Fit the shared model with curve_fit using equal-CSV log10-R2 residuals."""

    if starts < 1 or max_nfev < 1:
        raise ValueError("starts and max_nfev must be positive")

    try:
        from scipy.optimize import curve_fit
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "SciPy backend requires scipy. Install dependencies with:\n"
            "  python -m pip install -r Scripts/requirements-main-supp-n7.txt"
        ) from exc

    lower, upper = layout.bounds()
    log_scales = objective_row_scales(data)
    residual_count = data.observed_rpu.size
    dummy_x = np.arange(residual_count, dtype=float)
    zero_target = np.zeros(residual_count, dtype=float)

    def model(_: np.ndarray, *flat_parameters: float) -> np.ndarray:
        vector = np.asarray(flat_parameters)
        predicted, _terms = predict_rpu_numpy(data, layout, vector)
        predicted_log = log10_positive(predicted, "Predicted RPU")
        return (predicted_log - data.observed_log10) * log_scales

    best: tuple[float, np.ndarray, np.ndarray, int] | None = None
    failures: list[str] = []
    started = time.perf_counter()
    for start_index in range(max(1, starts)):
        p0 = layout.initial_vector(data, variant=start_index)
        try:
            popt, pcov = curve_fit(
                model,
                dummy_x,
                zero_target,
                p0=p0,
                bounds=(lower, upper),
                method="trf",
                max_nfev=max_nfev,
                ftol=1e-11,
                xtol=1e-11,
                gtol=1e-11,
            )
            components = objective_components_numpy(
                data, layout, popt, log_scales
            )
            objective = components["objective_total"]
            if best is None or objective < best[0]:
                best = (objective, popt, pcov, start_index)
        except Exception as exc:  # keep deterministic fallback starts auditable
            failures.append(f"start {start_index}: {type(exc).__name__}: {exc}")

    elapsed = time.perf_counter() - started
    if best is None:
        raise RuntimeError("All SciPy curve_fit starts failed:\n" + "\n".join(failures))
    objective, popt, pcov, best_start = best
    finite_covariance = bool(np.isfinite(pcov).all())
    components = objective_components_numpy(
        data, layout, popt, log_scales
    )
    return FitResult(
        backend=SCIPY_BACKEND,
        parameter_vector=popt,
        objective_total=objective,
        elapsed_seconds=elapsed,
        status="success",
        message=f"Best of {max(1, starts)} deterministic starts: {best_start}",
        diagnostics={
            "best_start": best_start,
            "start_failures": failures,
            "covariance_all_finite": finite_covariance,
            "max_nfev": max_nfev,
            "objective_components": components,
        },
    )


def cic_response_torch(inducer, ctf_all, Kd0, Kb, Kd1, KA, T0_variant, tmax=TMAX):
    """Differentiable version of the same stable n=7 equation; Torch is optional."""
    import torch

    B = 1.0 + Kb * inducer
    D = Kd0 + Kb.square() * Kd1 * inducer.square()
    S = torch.sqrt(B.square() + 8.0 * ctf_all * D)
    ctf_eff = D * (2.0 * ctf_all / (S + B)).square()
    Z = KA * ctf_eff
    p7 = -torch.expm1(-OPERATOR_NUMBER * torch.log1p(Z))
    return T0_variant + (tmax - T0_variant) * p7


def fit_pytorch(
    data: FitData,
    layout: ParameterLayout,
    epochs: int,
    learning_rate: float,
    patience: int,
    seed: int,
    initial_vector: np.ndarray | None = None,
    initialization_label: str = "layout_initial_vector_variant_0",
) -> FitResult:
    """Fit the same analytic model and equal-CSV log10-R2 objective with Adam."""

    if epochs < 1 or not np.isfinite(learning_rate) or learning_rate <= 0 or patience < 0:
        raise ValueError("epochs and learning_rate must be positive; patience must be non-negative")

    try:
        import torch
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "PyTorch backend requires torch. Install dependencies with:\n"
            "  python -m pip install -r requirements-torch.txt"
        ) from exc

    torch.manual_seed(seed)
    dtype = torch.float64
    device = torch.device("cpu")
    if initial_vector is None:
        initial_vector = layout.initial_vector(data, variant=0)
    initial_vector = np.asarray(initial_vector, dtype=float)
    layout.decode_numpy(initial_vector)
    initial_lower, initial_upper = layout.bounds()
    if np.any(initial_vector < initial_lower) or np.any(initial_vector > initial_upper):
        raise ValueError("PyTorch initial vector is outside the model bounds")
    if initial_vector.shape != (layout.size,):
        raise ValueError(
            f"PyTorch initial vector must have shape ({layout.size},); "
            f"got {initial_vector.shape}"
        )
    vector = torch.nn.Parameter(
        torch.tensor(initial_vector, dtype=dtype, device=device)
    )
    lower_np, upper_np = layout.bounds()
    lower = torch.tensor(lower_np, dtype=dtype, device=device)
    upper = torch.tensor(upper_np, dtype=dtype, device=device)

    ctf_all = torch.tensor(data.ctf_all, dtype=dtype, device=device)
    inducer = torch.tensor(data.inducer, dtype=dtype, device=device)
    observed_log10 = torch.tensor(data.observed_log10, dtype=dtype, device=device)
    log_scales_np = objective_row_scales(data)
    log_scales = torch.tensor(log_scales_np, dtype=dtype, device=device)
    lbd_index = torch.tensor(data.lbd_index, dtype=torch.long, device=device)
    dbd_index = torch.tensor(data.dbd_index, dtype=torch.long, device=device)
    anchor_index = layout.dbd_names.index(ANCHOR_DBD)
    free_dbd_indices = [
        layout.dbd_names.index(name) for name in layout.free_ka_dbd_names
    ]

    def torch_prediction() -> torch.Tensor:
        Kd0_all = torch.pow(10.0, vector[layout.log_Kd0])
        Kb_all = torch.pow(10.0, vector[layout.log_Kb])
        Kd1_all = torch.pow(10.0, vector[layout.log_Kd1])
        KA_all = torch.empty(len(layout.dbd_names), dtype=dtype, device=device)
        KA_all[anchor_index] = ANCHOR_KA
        KA_all[free_dbd_indices] = torch.pow(10.0, vector[layout.log_KA_free])
        T0_all = vector[layout.T0_variant]

        Kd0 = Kd0_all[lbd_index]
        Kb = Kb_all[lbd_index]
        Kd1 = Kd1_all[lbd_index]
        KA = KA_all[dbd_index]
        T0_variant = T0_all[dbd_index]
        return cic_response_torch(inducer, ctf_all, Kd0, Kb, Kd1, KA, T0_variant)

    def torch_objective() -> torch.Tensor:
        prediction = torch_prediction()
        if not torch.isfinite(prediction).all() or torch.any(prediction <= 0):
            raise RuntimeError("PyTorch predictions must be finite and strictly positive")
        return torch.sum(((torch.log10(prediction) - observed_log10) * log_scales).square())

    optimizer = torch.optim.Adam([vector], lr=learning_rate)
    best_loss = float("inf")
    best_vector = vector.detach().clone()
    best_epoch = 0
    stale_epochs = 0
    loss_trace: list[dict[str, float | int]] = []
    started = time.perf_counter()

    for epoch in range(1, epochs + 1):
        optimizer.zero_grad()
        loss = torch_objective()
        if not torch.isfinite(loss):
            raise RuntimeError(f"PyTorch loss became non-finite at epoch {epoch}")
        evaluated_vector = vector.detach().clone()
        loss.backward()
        torch.nn.utils.clip_grad_norm_([vector], max_norm=5.0)
        optimizer.step()
        with torch.no_grad():
            vector.clamp_(lower, upper)

        loss_value = float(loss.detach().cpu())
        if loss_value < best_loss - 1e-13:
            best_loss = loss_value
            best_vector = evaluated_vector
            best_epoch = epoch - 1
            stale_epochs = 0
        else:
            stale_epochs += 1

        if epoch == 1 or epoch % 5000 == 0:
            trace_row = {
                "completed_steps": epoch - 1,
                "objective_total": loss_value,
                "macro_log10_1_minus_R2": loss_value,
            }
            loss_trace.append(trace_row)
            print(
                f"[PyTorch/Adam] epoch={epoch} macro_log10_1_minus_R2={loss_value:.10g}"
            )
        if patience > 0 and stale_epochs >= patience:
            break

    # The last Adam step has not yet been evaluated by the loop. Consider it
    # explicitly, keeping the objective and its exact parameter vector paired.
    with torch.no_grad():
        final_loss = float(torch_objective().cpu())
        if not np.isfinite(final_loss):
            raise RuntimeError("PyTorch final loss became non-finite")
        if final_loss < best_loss:
            best_loss = final_loss
            best_vector = vector.detach().clone()
            best_epoch = epoch
    elapsed = time.perf_counter() - started
    best_vector_numpy = best_vector.cpu().numpy()
    components = objective_components_numpy(
        data,
        layout,
        best_vector_numpy,
        log_scales_np,
    )
    return FitResult(
        backend=TORCH_BACKEND,
        parameter_vector=best_vector_numpy,
        objective_total=components["objective_total"],
        elapsed_seconds=elapsed,
        status="patience" if patience > 0 and stale_epochs >= patience else "epoch_budget",
        message=(f"Best parameters after {best_epoch} Adam steps; completed {epoch} steps. "
                 "Stopping does not certify optimizer convergence."),
        diagnostics={
            "epochs_requested": epochs,
            "epochs_completed": epoch,
            "best_epoch": best_epoch,
            "learning_rate": learning_rate,
            "patience": patience,
            "seed": seed,
            "initialization": initialization_label,
            "loss_trace": loss_trace,
            "objective_components": components,
            "torch_objective_total": best_loss,
        },
    )


def r_squared(observed: np.ndarray, predicted: np.ndarray) -> float:
    residual_sum = float(np.sum((observed - predicted) ** 2))
    total_sum = float(np.sum((observed - np.mean(observed)) ** 2))
    return float("nan") if total_sum == 0 else 1.0 - residual_sum / total_sum


def metric_row(scope: str, observed: np.ndarray, predicted: np.ndarray) -> dict[str, object]:
    observed_log = log10_positive(observed, "Observed RPU")
    predicted_log = log10_positive(predicted, "Predicted RPU")
    return {
        "scope": scope,
        "n": int(observed.size),
        "R2_raw": r_squared(observed, predicted),
        "R2_log10": r_squared(observed_log, predicted_log),
        "RMSE_raw": float(np.sqrt(np.mean((observed - predicted) ** 2))),
        "RMSE_log10": float(np.sqrt(np.mean((observed_log - predicted_log) ** 2))),
        "MAE_raw": float(np.mean(np.abs(observed - predicted))),
        "MAE_log10": float(np.mean(np.abs(observed_log - predicted_log))),
    }


def build_metrics(data: FitData, predicted: np.ndarray) -> pd.DataFrame:
    rows = [metric_row("overall", data.observed_rpu, predicted)]
    for csv_index, mapping in enumerate(data.mappings):
        mask = data.csv_index == csv_index
        row = metric_row(mapping.csv_name, data.observed_rpu[mask], predicted[mask])
        row.update(
            {
                "sensor_name": mapping.sensor_name,
                "canonical_dbd": mapping.dbd,
                "canonical_lbd": mapping.lbd,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def make_curve_grid(frame: pd.DataFrame) -> np.ndarray:
    """Build a dense dose grid, including a real range for 0/high endpoint data."""

    observed = np.sort(frame["inducer"].astype(float).unique())
    positive = observed[observed > 0.0]
    if positive.size == 0:
        raise ValueError("Cannot generate an induction curve without a positive dose")
    maximum = float(positive[-1])
    if positive.size == 1 and np.any(observed == 0.0):
        minimum = maximum / (10.0**ZERO_ENDPOINT_GRID_DECADES)
    else:
        minimum = float(positive[0])
    minimum = max(minimum, np.finfo(float).tiny)
    positive_grid = np.logspace(
        math.log10(minimum), math.log10(maximum), CURVE_GRID_POINTS
    )
    if np.any(observed == 0.0):
        return np.concatenate(([0.0], positive_grid))
    return positive_grid


def synthetic_curve_data(
    mapping: SensorMapping,
    csv_index: int,
    ctf_value: float,
    grid: np.ndarray,
    layout: ParameterLayout,
) -> FitData:
    synthetic_frame = pd.DataFrame(
        {
            "LBD": np.full(grid.size, ctf_value),
            "inducer": grid,
            "RPU": np.ones(grid.size),
            "lbd_index": np.full(grid.size, layout.lbd_lookup[mapping.lbd]),
            "dbd_index": np.full(grid.size, layout.dbd_lookup[mapping.dbd]),
            "csv_index": np.full(grid.size, csv_index),
        }
    )
    return FitData(
        frame=synthetic_frame,
        mappings=[mapping],
        ctf_all=synthetic_frame["LBD"].to_numpy(dtype=float),
        inducer=synthetic_frame["inducer"].to_numpy(dtype=float),
        observed_rpu=np.ones(grid.size),
        observed_log10=np.zeros(grid.size),
        lbd_index=synthetic_frame["lbd_index"].to_numpy(dtype=int),
        dbd_index=synthetic_frame["dbd_index"].to_numpy(dtype=int),
        csv_index=synthetic_frame["csv_index"].to_numpy(dtype=int),
    )


def interpolate_fraction_dose(
    grid: np.ndarray, normalized: np.ndarray, fraction: float
) -> float:
    """Return a log-dose interpolation for a monotone normalized curve."""

    positive_mask = grid > 0.0
    x = grid[positive_mask]
    y = normalized[positive_mask]
    if x.size == 0 or fraction < float(np.min(y)) or fraction > float(np.max(y)):
        return float("nan")
    order = np.argsort(y)
    y_sorted = y[order]
    x_sorted = x[order]
    unique_y, unique_index = np.unique(y_sorted, return_index=True)
    if unique_y.size < 2:
        return float("nan")
    return float(
        10.0
        ** np.interp(fraction, unique_y, np.log10(x_sorted[unique_index]))
    )


def build_dense_curve_outputs(
    data: FitData,
    layout: ParameterLayout,
    vector: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dense_rows: list[pd.DataFrame] = []
    metric_rows: list[dict[str, object]] = []
    endpoint_indices = set(endpoint_only_lbd_indices(data, layout).tolist())
    for csv_index, mapping in enumerate(data.mappings):
        frame = data.frame.loc[data.csv_index == csv_index]
        grid = make_curve_grid(frame)
        observed_inducer_count = int(frame["inducer"].nunique())
        lbd_has_only_endpoints = layout.lbd_lookup[mapping.lbd] in endpoint_indices
        if observed_inducer_count > 2:
            source = "observed_complete_curve"
            identifiability = "direct"
        elif lbd_has_only_endpoints:
            source = "endpoint_only_unregularized"
            identifiability = "limited"
        else:
            source = "shared_complete_curve_LBD"
            identifiability = "shared"
        for ctf_value in sorted(frame["LBD"].unique()):
            synthetic = synthetic_curve_data(
                mapping, csv_index, float(ctf_value), grid, layout
            )
            curve, terms = predict_rpu_numpy(synthetic, layout, vector)
            dense = pd.DataFrame(
                {
                    "csv": mapping.csv_name,
                    "sensor_name": mapping.sensor_name,
                    "canonical_dbd": mapping.dbd,
                    "canonical_lbd": mapping.lbd,
                    "LBD": float(ctf_value),
                    "inducer": grid,
                    "RPU_predicted": curve,
                    "curve_shape_source": source,
                    "curve_shape_identifiability": identifiability,
                }
            )
            for name, values in terms.items():
                dense[name] = values
            dense_rows.append(dense)

            amplitude = float(curve[-1] - curve[0])
            if abs(amplitude) > 1e-15:
                normalized = (curve - curve[0]) / amplitude
                c10 = interpolate_fraction_dose(grid, normalized, 0.1)
                c50 = interpolate_fraction_dose(grid, normalized, 0.5)
                c90 = interpolate_fraction_dose(grid, normalized, 0.9)
            else:
                c10 = c50 = c90 = float("nan")
            transition_decades = (
                float(math.log10(c90 / c10))
                if np.isfinite(c10) and np.isfinite(c90) and c10 > 0.0
                else float("nan")
            )
            tolerance = max(abs(amplitude), 1.0) * 1e-10
            metric_rows.append(
                {
                    "csv": mapping.csv_name,
                    "sensor_name": mapping.sensor_name,
                    "canonical_dbd": mapping.dbd,
                    "canonical_lbd": mapping.lbd,
                    "LBD": float(ctf_value),
                    "observed_inducer_levels": observed_inducer_count,
                    "curve_grid_points": int(grid.size),
                    "curve_grid_min_positive": float(np.min(grid[grid > 0.0])),
                    "curve_grid_max": float(np.max(grid)),
                    "curve_shape_source": source,
                    "curve_shape_identifiability": identifiability,
                    "RPU_curve_low": float(curve[0]),
                    "RPU_curve_high": float(curve[-1]),
                    "RPU_curve_amplitude": amplitude,
                    "dose_10_percent": c10,
                    "dose_50_percent": c50,
                    "dose_90_percent": c90,
                    "transition_width_log10_decades": transition_decades,
                    "monotone_nondecreasing": bool(np.all(np.diff(curve) >= -tolerance)),
                    "linear_endpoint_interpolation": False,
                }
            )
    return pd.concat(dense_rows, ignore_index=True), pd.DataFrame(metric_rows)


def write_result(
    result: FitResult,
    data: FitData,
    layout: ParameterLayout,
    output_root: Path,
) -> dict[str, object]:
    parameters = layout.decode_numpy(result.parameter_vector)
    lower, upper = layout.bounds()
    if np.any(result.parameter_vector < lower) or np.any(result.parameter_vector > upper):
        raise ValueError("Saved parameter vector is outside the model bounds")
    objective_components = objective_components_numpy(data, layout, result.parameter_vector)
    if not np.isclose(result.objective_total, objective_components["objective_total"], rtol=1e-10, atol=1e-12):
        raise ValueError("Fit objective does not match the saved parameter vector")
    predicted, terms = predict_rpu_numpy(data, layout, result.parameter_vector)

    if not np.all(np.isfinite(predicted)):
        raise RuntimeError(f"{result.backend} produced non-finite predictions")
    if np.any(predicted <= 0) or np.any(predicted > TMAX + 1e-9):
        raise RuntimeError(
            f"{result.backend} predictions violate 0 < T(x) <= Tmax={TMAX}"
        )
    if not np.all((terms["p7"] >= -1e-12) & (terms["p7"] <= 1 + 1e-12)):
        raise RuntimeError(f"{result.backend} produced invalid seven-operator occupancy")

    endpoint_indices = set(endpoint_only_lbd_indices(data, layout).tolist())
    lbd_table = pd.DataFrame(
        {
            "canonical_lbd": layout.lbd_names,
            "Kd0": parameters.Kd0,
            "Kb_uM_inverse": parameters.Kb,
            "Kd1": parameters.Kd1,
            "Q_LBD_Kb2_Kd1_over_Kd0": (
                parameters.Kb**2 * parameters.Kd1 / parameters.Kd0
            ),
            "has_complete_induction_curve": [
                index not in endpoint_indices for index in range(len(layout.lbd_names))
            ],
        }
    )
    dbd_table = pd.DataFrame(
        {
            "canonical_dbd": layout.dbd_names,
            "KA": parameters.KA,
            "KA_fixed": [name == ANCHOR_DBD for name in layout.dbd_names],
            "T0_variant": parameters.T0_variant,
            "Tmax": TMAX,
            "output_amplitude_Tmax_minus_T0": TMAX - parameters.T0_variant,
            "operator_number": OPERATOR_NUMBER,
        }
    )
    prediction_table = data.frame.copy()
    prediction_table["RPU_predicted"] = predicted
    prediction_table["log10_RPU_observed"] = data.observed_log10
    prediction_table["log10_RPU_predicted"] = np.log10(predicted)
    prediction_table["residual_raw"] = data.observed_rpu - predicted
    prediction_table["residual_log10"] = data.observed_log10 - np.log10(predicted)
    for name, values in terms.items():
        prediction_table[name] = values
    metrics = build_metrics(data, predicted)
    per_csv_metrics = metrics.loc[metrics["scope"] != "overall"]
    macro_metrics = {
        "R2_raw": float(per_csv_metrics["R2_raw"].mean()),
        "R2_log10": float(per_csv_metrics["R2_log10"].mean()),
        "RMSE_raw": float(per_csv_metrics["RMSE_raw"].mean()),
        "RMSE_log10": float(per_csv_metrics["RMSE_log10"].mean()),
        "MAE_raw": float(per_csv_metrics["MAE_raw"].mean()),
        "MAE_log10": float(per_csv_metrics["MAE_log10"].mean()),
    }
    backend_dir = output_root / result.backend
    backend_dir.mkdir(parents=True, exist_ok=True)
    lbd_table.to_csv(backend_dir / "parameters_lbd.csv", index=False)
    dbd_table.to_csv(backend_dir / "parameters_dbd.csv", index=False)
    prediction_table.to_csv(backend_dir / "predictions.csv", index=False)
    metrics.to_csv(backend_dir / "metrics.csv", index=False)
    pd.DataFrame([macro_metrics]).to_csv(backend_dir / "macro_metrics.csv", index=False)
    pd.DataFrame([objective_components]).to_csv(
        backend_dir / "objective_components.csv", index=False
    )
    np.save(backend_dir / "parameter_vector.npy", result.parameter_vector)

    # Keep the JSON summary standards-compliant: the descriptive columns are
    # intentionally empty in the overall CSV row, but JSON must not contain NaN.
    overall_metric_names = (
        "scope",
        "n",
        "R2_raw",
        "R2_log10",
        "RMSE_raw",
        "RMSE_log10",
        "MAE_raw",
        "MAE_log10",
    )
    overall = {name: metrics.iloc[0][name] for name in overall_metric_names}
    summary = {
        "backend": result.backend,
        "status": result.status,
        "message": result.message,
        "objective": OBJECTIVE_DESCRIPTION,
        "objective_total": objective_components["objective_total"],
        "objective_components": objective_components,
        "CSV_weighting": "equal macro average across included CSVs",
        "R2_raw_role": "diagnostic only",
        "elapsed_seconds": result.elapsed_seconds,
        "Tmax": TMAX,
        "operator_number": OPERATOR_NUMBER,
        "anchor_DBD": ANCHOR_DBD,
        "anchor_KA": ANCHOR_KA,
        "included_CSV_count": len(data.mappings),
        "excluded_CSV": sorted(EXCLUDED_CSV),
        "LBD_parameter_groups": len(layout.lbd_names),
        "DBD_parameter_groups": len(layout.dbd_names),
        "free_parameter_count": layout.size,
        "overall_metrics": overall,
        "macro_metrics": macro_metrics,
        "diagnostics": result.diagnostics,
    }
    (backend_dir / "fit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=float) + "\n",
        encoding="utf-8",
    )
    return summary


def write_comparison(output_root: Path, summaries: Sequence[dict[str, object]]) -> None:
    rows: list[dict[str, object]] = []
    for summary in summaries:
        metrics = dict(summary["overall_metrics"])
        macro = dict(summary["macro_metrics"])
        components = dict(summary["objective_components"])
        rows.append(
            {
                "backend": summary["backend"],
                "objective_total": summary["objective_total"],
                "data_objective": components["data_objective"],
                "macro_R2_raw": macro["R2_raw"],
                "macro_R2_log10": macro["R2_log10"],
                "global_R2_raw": metrics["R2_raw"],
                "global_R2_log10": metrics["R2_log10"],
                "global_RMSE_raw": metrics["RMSE_raw"],
                "global_RMSE_log10": metrics["RMSE_log10"],
                "elapsed_seconds": summary["elapsed_seconds"],
            }
        )
    pd.DataFrame(rows).to_csv(
        output_root / "backend_comparison_macro_log10_r2.csv", index=False
    )


def print_mapping_summary(mappings: Iterable[SensorMapping]) -> None:
    for mapping in mappings:
        status = "included" if mapping.included else "excluded control"
        print(
            f"{mapping.csv_name}: {mapping.sensor_name} | "
            f"DBD={mapping.dbd} | LBD={mapping.lbd} | {status}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fit the seven-operator mammalian CIC model by macro per-CSV log10 R2."
    )
    parser.add_argument(
        "--backend",
        choices=("scipy", "torch", "both"),
        default="both",
        help="Fitting backend; default: both.",
    )
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--list-mappings", action="store_true")
    parser.add_argument("--scipy-starts", type=int, default=3)
    parser.add_argument("--max-nfev", type=int, default=500_000_000)
    parser.add_argument("--torch-epochs", type=int, default=100_000)
    parser.add_argument("--torch-learning-rate", type=float, default=0.001)
    parser.add_argument("--torch-patience", type=int, default=15_000)
    parser.add_argument("--seed", type=int, default=20260818)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    readme_path = args.readme.resolve()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()

    mappings = read_sensor_mapping(readme_path)
    print(f"README: {readme_path}")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print_mapping_summary(mappings)
    if args.list_mappings:
        return

    data = load_fit_data(input_dir, mappings)
    layout = ParameterLayout(data.mappings)
    print(
        f"Loaded {len(data.frame)} observations from {len(data.mappings)} CIC CSVs; "
        f"{len(layout.lbd_names)} LBD groups; {len(layout.dbd_names)} DBD groups; "
        f"{layout.size} free parameters."
    )
    print(
        f"Fixed: KA_{ANCHOR_DBD}={ANCHOR_KA}, Tmax={TMAX}, "
        f"operator_number={OPERATOR_NUMBER}; objective={OBJECTIVE_DESCRIPTION}."
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, object]] = []
    scipy_result: FitResult | None = None
    if args.backend in {"scipy", "both"}:
        print("Starting SciPy curve_fit backend...")
        scipy_result = fit_scipy(
            data,
            layout,
            max_nfev=args.max_nfev,
            starts=args.scipy_starts,
        )
        summaries.append(write_result(scipy_result, data, layout, output_dir))
        print(
            f"SciPy complete: objective={scipy_result.objective_total:.8g}; "
            f"elapsed={scipy_result.elapsed_seconds:.1f}s"
        )
    if args.backend in {"torch", "both"}:
        print("Starting PyTorch/Adam backend...")
        torch_initial = (
            scipy_result.parameter_vector if scipy_result is not None else None
        )
        torch_initialization = (
            f"warm_start_from_{SCIPY_BACKEND}"
            if scipy_result is not None
            else "layout_initial_vector_variant_0"
        )
        torch_result = fit_pytorch(
            data,
            layout,
            epochs=args.torch_epochs,
            learning_rate=args.torch_learning_rate,
            patience=args.torch_patience,
            seed=args.seed,
            initial_vector=torch_initial,
            initialization_label=torch_initialization,
        )
        summaries.append(write_result(torch_result, data, layout, output_dir))
        print(
            f"PyTorch complete: objective={torch_result.objective_total:.8g}; "
            f"elapsed={torch_result.elapsed_seconds:.1f}s"
        )

    write_comparison(output_dir, summaries)
    print(f"Results written to: {output_dir}")


if __name__ == "__main__":
    main()
