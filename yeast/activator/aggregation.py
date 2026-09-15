"""Separate batch-specific R2 observations from the source plotting pools."""
from __future__ import annotations
import math
import statistics
from .panels import PANELS
from .parameters import dbd_parameters_for_panel
from .settings import TMAX_PRIMARY, TMAX_ALTERNATE, GLOBAL_T0_SENSITIVITY, PLOT_INPUT_RELATIVE_TOLERANCE
from .model import model_s32_s47, model_s83_literal, unit_factor


def conditional_means(raw_rows, dbd_params, lbd_params, panels=PANELS):
    # R2 observation unit: a conditional mean within one experimental batch at
    # exactly the same measured TF input and inducer concentration. Batch is a
    # mandatory part of the key, so separate batches are never averaged for R2.
    condition_groups: dict[tuple, list[dict]] = {}
    for row in raw_rows:
        if not row["included_primary"]:
            continue
        key = (
            row["panel_id"], row["plot_type"], row["batch_id"],
            row["actual_input_rpu"], row["nominal_input_rpu"],
            row["inducer_concentration_source"], row["inducer_source_unit"],
            row["inducer_concentration_uM"],
        )
        condition_groups.setdefault(key, []).append(row)

    condition_rows: list[dict] = []
    panel_by_id = {p.panel_id: p for p in panels}
    for key, group in condition_groups.items():
        panel_id, plot_type, batch_id, ctf, nominal_ctf, dose_source, source_unit, dose_uM = key
        panel = panel_by_id[panel_id]
        responses = [float(row["response_rpu"]) for row in group]
        sd = statistics.stdev(responses) if len(responses) > 1 else float("nan")
        dp = dbd_parameters_for_panel(panel, dbd_params)
        lp = lbd_params[panel.lbd]
        prediction = float(model_s32_s47(ctf, dose_uM, dp["KA"], lp["Kd0"], lp["Kb"], lp["Kd1"], dp["T0_variant"], TMAX_PRIMARY))
        prediction_tmax35 = float(model_s32_s47(ctf, dose_uM, dp["KA"], lp["Kd0"], lp["Kb"], lp["Kd1"], dp["T0_variant"], TMAX_ALTERNATE))
        prediction_global_t0 = float(model_s32_s47(ctf, dose_uM, dp["KA"], lp["Kd0"], lp["Kb"], lp["Kd1"], GLOBAL_T0_SENSITIVITY, TMAX_PRIMARY))
        prediction_literal = float(model_s83_literal(ctf, dose_uM, dp["KA"], lp["Kd0"], lp["Kb"], lp["Kd1"], dp["T0_variant"], TMAX_PRIMARY))
        condition_rows.append({
            "panel_id": panel_id,
            "page": panel.page,
            "panel_order": panel.order,
            "construct": panel.construct,
            "dbd": panel.dbd,
            "operator": panel.operator,
            "lbd": panel.lbd,
            "inducer": panel.inducer,
            "plot_type": plot_type,
            "input_rpu": ctf,
            "actual_input_rpu": ctf,
            "nominal_input_rpu": nominal_ctf,
            "batch_id": batch_id,
            "inducer_concentration_source": dose_source,
            "inducer_source_unit": source_unit,
            "inducer_to_uM_factor": unit_factor(source_unit),
            "inducer_concentration_uM": dose_uM,
            "n_included": len(responses),
            "mean_response_rpu": statistics.fmean(responses),
            "sd_response_rpu": sd,
            "sem_response_rpu": sd / math.sqrt(len(responses)) if len(responses) > 1 else float("nan"),
            "KA": dp["KA"],
            "T0_variant": dp["T0_variant"],
            "Kd0": lp["Kd0"],
            "Kb_per_uM": lp["Kb"],
            "Kd1": lp["Kd1"],
            "Tmax_primary": TMAX_PRIMARY,
            "prediction_primary_rpu": prediction,
            "prediction_Tmax35_rpu": prediction_tmax35,
            "prediction_global_T0_0_035_rpu": prediction_global_t0,
            "prediction_literal_S83_rpu": prediction_literal,
            "source_cells": ";".join(row["source_cell"] for row in group),
            "aggregation_rule": "within-batch arithmetic conditional mean of non-starred replicates at identical actual TF input and inducer; batches never pooled",
        })


    return condition_rows


def plot_summaries(raw_rows, dbd_params, lbd_params, panels=PANELS):
    panel_by_id = {panel.panel_id: panel for panel in panels}
    # Plot observation unit: cluster batch-specific measured TF inputs within
    # each panel. A nonzero cluster is valid only when every member differs by
    # <=30% from that cluster's arithmetic-mean input. Source-designated zero
    # batches are one categorical zero cluster because relative error at zero
    # is undefined. This plotting pool never changes the R2 observation unit.
    dose_batches_by_panel: dict[str, dict[str, dict]] = {}
    for row in raw_rows:
        if row["plot_type"] != "dose_response":
            continue
        dose_batches_by_panel.setdefault(row["panel_id"], {})[row["batch_id"]] = {
            "batch_id": row["batch_id"],
            "actual_input_rpu": float(row["actual_input_rpu"]),
            "nominal_input_rpu": float(row["nominal_input_rpu"]),
        }

    cluster_by_batch: dict[tuple[str, str], dict] = {}
    plot_input_audit_rows: list[dict] = []
    for panel in panels:
        batch_records = list(dose_batches_by_panel.get(panel.panel_id, {}).values())
        zero_records = [
            row for row in batch_records
            if row["nominal_input_rpu"] == 0 or row["actual_input_rpu"] <= 0
        ]
        positive_records = sorted(
            [row for row in batch_records if row not in zero_records],
            key=lambda row: row["actual_input_rpu"],
        )
        clusters: list[list[dict]] = []
        if zero_records:
            clusters.append(zero_records)
        for record in positive_records:
            if not clusters or clusters[-1] is zero_records:
                clusters.append([record])
                continue
            candidate = clusters[-1] + [record]
            center = statistics.fmean(item["actual_input_rpu"] for item in candidate)
            maximum_deviation = max(
                abs(item["actual_input_rpu"] - center) / center for item in candidate
            )
            if maximum_deviation <= PLOT_INPUT_RELATIVE_TOLERANCE + 1e-12:
                clusters[-1].append(record)
            else:
                clusters.append([record])

        for cluster_number, cluster in enumerate(clusters, start=1):
            is_zero_cluster = any(item in zero_records for item in cluster)
            center = 0.0 if is_zero_cluster else statistics.fmean(
                item["actual_input_rpu"] for item in cluster
            )
            maximum_deviation = 0.0 if is_zero_cluster else max(
                abs(item["actual_input_rpu"] - center) / center for item in cluster
            )
            cluster_id = f"plot_input_cluster_{cluster_number}"
            for item in cluster:
                mapping = {
                    "cluster_id": cluster_id,
                    "plot_input_rpu": center,
                    "cluster_size_batches": len(cluster),
                    "cluster_max_relative_deviation": maximum_deviation,
                    "status": "ZERO_REFERENCE_SOURCE_GROUP" if is_zero_cluster else "WITHIN_30_PERCENT_CLUSTER",
                }
                cluster_by_batch[(panel.panel_id, item["batch_id"])] = mapping
                plot_input_audit_rows.append({
                    "panel_id": panel.panel_id,
                    "page": panel.page,
                    "plot_type": "dose_response",
                    "batch_id": item["batch_id"],
                    "source_nominal_input_rpu": item["nominal_input_rpu"],
                    "actual_input_rpu": item["actual_input_rpu"],
                    "plot_input_cluster_id": cluster_id,
                    "plot_input_cluster_mean_rpu": center,
                    "batch_relative_deviation_from_cluster_mean": (
                        0.0 if is_zero_cluster else abs(item["actual_input_rpu"] - center) / center
                    ),
                    "cluster_max_relative_deviation": maximum_deviation,
                    "tolerance": PLOT_INPUT_RELATIVE_TOLERANCE,
                    "included_in_plot_pool": True,
                    "status": mapping["status"],
                    "rule": "nonzero batch inputs clustered only when every member is within 30% of cluster arithmetic mean; source-designated zero batches form the zero cluster",
                })

    plot_groups: dict[tuple, list[dict]] = {}
    for row in raw_rows:
        if not row["included_primary"]:
            continue
        if row["plot_type"] == "dose_response":
            cluster = cluster_by_batch[(row["panel_id"], row["batch_id"])]
            plot_input = cluster["plot_input_rpu"]
            cluster_id = cluster["cluster_id"]
        else:
            plot_input = float(row["actual_input_rpu"])
            cluster_id = row["batch_id"]
        key = (
            row["panel_id"], row["plot_type"], cluster_id, plot_input,
            row["inducer_concentration_source"], row["inducer_source_unit"],
            row["inducer_concentration_uM"],
        )
        plot_groups.setdefault(key, []).append(row)

    plot_rows: list[dict] = []
    for key, group in plot_groups.items():
        panel_id, plot_type, cluster_id, plot_ctf, dose_source, source_unit, dose_uM = key
        panel = panel_by_id[panel_id]
        responses = [float(row["response_rpu"]) for row in group]
        sd = statistics.stdev(responses) if len(responses) > 1 else float("nan")
        batch_inputs = {
            (row["batch_id"], float(row["actual_input_rpu"]))
            for row in group
        }
        actual_inputs = [actual for _, actual in sorted(batch_inputs)]
        dp = dbd_parameters_for_panel(panel, dbd_params)
        lp = lbd_params[panel.lbd]
        prediction = float(model_s32_s47(
            plot_ctf, dose_uM, dp["KA"], lp["Kd0"], lp["Kb"], lp["Kd1"],
            dp["T0_variant"], TMAX_PRIMARY,
        ))
        plot_rows.append({
            "panel_id": panel_id,
            "page": panel.page,
            "panel_order": panel.order,
            "construct": panel.construct,
            "dbd": panel.dbd,
            "operator": panel.operator,
            "lbd": panel.lbd,
            "inducer": panel.inducer,
            "plot_type": plot_type,
            "input_rpu": plot_ctf,
            "plot_input_cluster_id": cluster_id,
            "plot_input_cluster_mean_rpu": plot_ctf,
            "source_nominal_inputs_rpu": ";".join(
                f"{value:.12g}" for value in sorted({float(row["nominal_input_rpu"]) for row in group})
            ),
            "mean_actual_batch_input_rpu": statistics.fmean(actual_inputs),
            "min_actual_batch_input_rpu": min(actual_inputs),
            "max_actual_batch_input_rpu": max(actual_inputs),
            "batch_ids": ";".join(batch for batch, _ in sorted(batch_inputs)),
            "batch_actual_inputs_rpu": ";".join(f"{actual:.12g}" for actual in actual_inputs),
            "n_batches": len(batch_inputs),
            "inducer_concentration_source": dose_source,
            "inducer_source_unit": source_unit,
            "inducer_to_uM_factor": unit_factor(source_unit),
            "inducer_concentration_uM": dose_uM,
            "n_included": len(responses),
            "mean_response_rpu": statistics.fmean(responses),
            "sd_response_rpu": sd,
            "sem_response_rpu": sd / math.sqrt(len(responses)) if len(responses) > 1 else float("nan"),
            "KA": dp["KA"],
            "T0_variant": dp["T0_variant"],
            "Kd0": lp["Kd0"],
            "Kb_per_uM": lp["Kb"],
            "Kd1": lp["Kd1"],
            "Tmax_primary": TMAX_PRIMARY,
            "prediction_primary_rpu": prediction,
            "aggregation_rule": "plot mean +/- sample SD after pooling non-starred outputs at identical inducer across measured TF-input batches whose inputs are all within 30% of the cluster arithmetic mean; source-zero batches pooled as zero",
        })


    return plot_rows, plot_input_audit_rows
