"""Read source-layout measurements without pooling experimental batches."""
from __future__ import annotations
import math
import re
from typing import Iterable
from .panels import PANELS, Panel
from .settings import PLOT_INPUT_RELATIVE_TOLERANCE
from .source import parse_cell, clean_number, excel_col
from .model import unit_factor


def extract_measurements(values, green_cells, panels=PANELS):
    def is_green_cell(row, column):
        return (row, column) in green_cells

    raw_rows: list[dict] = []

    def append_raw(
        panel: Panel,
        plot_type: str,
        ctf: float,
        dose_source: float,
        replicate: int,
        value,
        r0: int,
        c0: int,
        replicate_group: str,
        nominal_ctf: float | None = None,
        batch_id: str | None = None,
    ) -> None:
        numeric, starred = parse_cell(value)
        if numeric is None:
            if value is not None and str(value).strip():
                raise ValueError(f"Non-numeric response at {excel_col(c0)}{r0 + 1}: {value!r}")
            return
        if not all(math.isfinite(x) and x >= 0 for x in (ctf, dose_source)):
            raise ValueError(f"Invalid concentration at {excel_col(c0)}{r0 + 1}")
        factor = unit_factor(panel.dose_unit)
        green_fill = is_green_cell(r0, c0)
        nominal = float(ctf if nominal_ctf is None else nominal_ctf)
        actual = float(ctf)
        if nominal == 0:
            input_relative_deviation = 0.0 if actual == 0 else float("nan")
            plot_input_tolerance_status = "ZERO_REFERENCE_SOURCE_GROUP"
            included_plot_30pct = True
        else:
            input_relative_deviation = abs(actual - nominal) / abs(nominal)
            included_plot_30pct = input_relative_deviation <= PLOT_INPUT_RELATIVE_TOLERANCE + 1e-12
            plot_input_tolerance_status = "WITHIN_30_PERCENT" if included_plot_30pct else "OUTSIDE_30_PERCENT"
        raw_rows.append({
            "panel_id": panel.panel_id,
            "page": panel.page,
            "panel_order": panel.order,
            "construct": panel.construct,
            "dbd": panel.dbd,
            "operator": panel.operator,
            "lbd": panel.lbd,
            "inducer": panel.inducer,
            "source_sheet": "SI-note activator",
            "source_cell": f"{excel_col(c0)}{r0 + 1}",
            "plot_type": plot_type,
            "input_rpu": actual,
            "actual_input_rpu": actual,
            "nominal_input_rpu": nominal,
            "input_relative_deviation_from_nominal": input_relative_deviation,
            "plot_input_tolerance_status": plot_input_tolerance_status,
            "included_plot_30pct": included_plot_30pct,
            "inducer_concentration_source": float(dose_source),
            "inducer_source_unit": panel.dose_unit,
            "inducer_to_uM_factor": factor,
            "inducer_concentration_uM": float(dose_source) * factor,
            "replicate": replicate,
            "replicate_group": replicate_group,
            "batch_id": batch_id or replicate_group,
            "response_rpu": numeric,
            "starred_in_workbook": starred,
            "green_fill_in_workbook": green_fill,
            "included_primary": not starred,
            "included_green_exclusion_sensitivity": (not starred) and (not green_fill),
            "exclusion_reason": "source cell has trailing *; meaning not defined in supplied manuscript" if starred else "",
        })

    def dose_batch_segments(header_row: int, group_start: int, width: int, nominal_ctf: float) -> list[tuple[int, int, float, int]]:
        """Return (start_col, end_col_exclusive, actual_input, batch_number).

        Numeric cells in the source dose-response header mark the beginning of
        a distinct experimental batch. Blank cells to the right are replicate
        output columns for that batch, ending at the next numeric header or the
        end of the nominal-input block.
        """
        numeric_headers: list[tuple[int, float]] = []
        for c0 in range(group_start, group_start + width):
            number, _ = parse_cell(values[header_row][c0])
            if number is not None:
                numeric_headers.append((c0, float(number)))
        if not numeric_headers or numeric_headers[0][0] != group_start:
            numeric_headers.insert(0, (group_start, float(nominal_ctf)))
        segments: list[tuple[int, int, float, int]] = []
        for batch_index, (start_col, actual_input) in enumerate(numeric_headers, start=1):
            end_col = numeric_headers[batch_index][0] if batch_index < len(numeric_headers) else group_start + width
            segments.append((start_col, end_col, actual_input, batch_index))
        return segments

    def append_dose_matrix(
        panel: Panel,
        header_row: int,
        response_rows: Iterable[int],
        dose_col: int,
        group_starts: list[int],
        group_widths: list[int],
        nominal_inputs: list[float],
        batch_suffix: str = "",
    ) -> None:
        for r0 in response_rows:
            dose = clean_number(values[r0][dose_col])
            for input_index, (group_start, width, nominal_ctf) in enumerate(
                zip(group_starts, group_widths, nominal_inputs), start=1
            ):
                for start_col, end_col, actual_ctf, batch_number in dose_batch_segments(
                    header_row, group_start, width, nominal_ctf
                ):
                    batch_id = f"dose_input_{input_index}_batch_{batch_number}{batch_suffix}"
                    for replicate, c0 in enumerate(range(start_col, end_col), start=1):
                        append_raw(
                            panel, "dose_response", actual_ctf, dose, replicate,
                            values[r0][c0], r0, c0, f"dose_input_{input_index}",
                            nominal_ctf=nominal_ctf, batch_id=batch_id,
                        )

    def append_ordinal_labeled_dose_matrix(
        panel: Panel,
        label_row: int,
        response_rows: Iterable[int],
        dose_col: int,
        group_starts: list[int],
        group_widths: list[int],
        nominal_inputs: list[float],
    ) -> None:
        """Append DBD matrices whose batch and actual input are text labels.

        The source encodes each batch twice, once over each replicate column,
        for example ``2nd (0.134259)`` in two adjacent cells.  The leading two
        columns in each eight-column nominal-input block are blank.  Each
        distinct ordinal label is therefore one experimental batch with two
        replicate columns; it must not be pooled with the other ordinals.
        """
        label_pattern = re.compile(
            r"^\s*(\d+)(?:st|nd|rd|th)\s*\(\s*([-+0-9.eE]+)\s*\)\s*$",
            re.IGNORECASE,
        )
        segments_by_input: list[list[tuple[int, int, float, int]]] = []
        for group_start, width in zip(group_starts, group_widths):
            segments: list[tuple[int, int, float, int]] = []
            current: tuple[int, float] | None = None
            start_col: int | None = None
            last_col: int | None = None
            for c0 in range(group_start, group_start + width):
                match = label_pattern.match(str(values[label_row][c0] or ""))
                if match is None:
                    continue
                identity = (int(match.group(1)), float(match.group(2)))
                if current is None:
                    current, start_col = identity, c0
                elif identity != current or (last_col is not None and c0 != last_col + 1):
                    if start_col is None or last_col is None:
                        raise ValueError("Incomplete ordinal batch segment")
                    segments.append((start_col, last_col + 1, current[1], current[0]))
                    current, start_col = identity, c0
                last_col = c0
            if current is not None:
                if start_col is None or last_col is None:
                    raise ValueError("Incomplete ordinal batch segment")
                segments.append((start_col, last_col + 1, current[1], current[0]))
            if not segments:
                raise ValueError(
                    f"No ordinal batch labels found for {panel.panel_id} "
                    f"at row {label_row + 1}, columns {group_start + 1}:{group_start + width}"
                )
            segments_by_input.append(segments)

        for r0 in response_rows:
            dose = clean_number(values[r0][dose_col])
            for input_index, (segments, nominal_ctf) in enumerate(
                zip(segments_by_input, nominal_inputs), start=1
            ):
                for start_col, end_col, actual_ctf, batch_number in segments:
                    batch_id = f"dose_input_{input_index}_batch_{batch_number}"
                    for replicate, c0 in enumerate(range(start_col, end_col), start=1):
                        append_raw(
                            panel, "dose_response", actual_ctf, dose, replicate,
                            values[r0][c0], r0, c0, f"dose_input_{input_index}",
                            nominal_ctf=nominal_ctf, batch_id=batch_id,
                        )

    def append_actual_labeled_dose_matrix(
        panel: Panel,
        actual_input_row: int,
        label_row: int,
        response_rows: Iterable[int],
        dose_col: int,
        group_starts: list[int],
        group_widths: list[int],
        nominal_inputs: list[float],
        batch_kind: str,
    ) -> None:
        """Append Run/Day matrices using explicit batch-specific TF inputs."""
        label_pattern = re.compile(rf"^\s*{re.escape(batch_kind)}(\d+)\b", re.IGNORECASE)
        segments_by_input: list[list[tuple[int, int, float, int, int]]] = []
        for group_start, width in zip(group_starts, group_widths):
            numeric_headers: list[tuple[int, float, int]] = []
            for c0 in range(group_start, group_start + width):
                actual_input, _ = parse_cell(values[actual_input_row][c0])
                if actual_input is None:
                    continue
                match = label_pattern.match(str(values[label_row][c0] or ""))
                if match is None:
                    raise ValueError(
                        f"Actual input header without {batch_kind} label for {panel.panel_id} "
                        f"at {excel_col(c0)}{label_row + 1}"
                    )
                numeric_headers.append((c0, float(actual_input), int(match.group(1))))
            if not numeric_headers:
                raise ValueError(
                    f"No batch-specific actual inputs found for {panel.panel_id} "
                    f"at row {actual_input_row + 1}"
                )
            seen_labels: dict[int, int] = {}
            segments: list[tuple[int, int, float, int, int]] = []
            for header_index, (start_col, actual_input, source_batch_number) in enumerate(numeric_headers):
                end_col = (
                    numeric_headers[header_index + 1][0]
                    if header_index + 1 < len(numeric_headers)
                    else group_start + width
                )
                seen_labels[source_batch_number] = seen_labels.get(source_batch_number, 0) + 1
                segments.append(
                    (start_col, end_col, actual_input, source_batch_number, seen_labels[source_batch_number])
                )
            segments_by_input.append(segments)

        suffix = f"_{batch_kind.lower()}"
        for r0 in response_rows:
            dose = clean_number(values[r0][dose_col])
            for input_index, (segments, nominal_ctf) in enumerate(
                zip(segments_by_input, nominal_inputs), start=1
            ):
                for start_col, end_col, actual_ctf, batch_number, occurrence in segments:
                    repeat_suffix = f"_repeat_{occurrence}" if occurrence > 1 else ""
                    batch_id = (
                        f"dose_input_{input_index}_batch_{batch_number}{suffix}{repeat_suffix}"
                    )
                    for replicate, c0 in enumerate(range(start_col, end_col), start=1):
                        append_raw(
                            panel, "dose_response", actual_ctf, dose, replicate,
                            values[r0][c0], r0, c0, f"dose_input_{input_index}{suffix}",
                            nominal_ctf=nominal_ctf, batch_id=batch_id,
                        )

    for panel in panels:
        start = panel.block_row - 1
        if panel.source_kind == "DBD":
            if panel.dbd.startswith("CI94-"):
                # CI94 blocks store six target input levels in column A.  The
                # dose matrix has six response columns per target level; its
                # header also contains sub-run measured input values, which are
                # provenance values rather than six additional curve identities.
                header_row = start + 1
                left_first = start + 2
                ctf_values = [clean_number(values[left_first + j][0]) for j in range(6)]
                dose_rows = range(start + 2, start + 10)
                for j, ctf in enumerate(ctf_values):
                    r0 = left_first + j
                    for k in range(6):
                        append_raw(panel, "input_output_off", ctf, 0.0, k + 1, values[r0][1 + k], r0, 1 + k, "left_off")
                        append_raw(panel, "input_output_on", ctf, 100.0, k + 1, values[r0][7 + k], r0, 7 + k, "left_on")
                append_dose_matrix(
                    panel, header_row, dose_rows, 19,
                    [20 + 6 * j for j in range(6)], [6] * 6, ctf_values,
                )
            elif panel.dbd == "LexAbs94":
                ctf_values = [clean_number(values[start + 2 + j][0]) for j in range(6)]
                header = values[start + 2]
                group_width = 6 if all(parse_cell(header[20 + 6 * j])[0] is not None for j in range(6)) else 3
                for j, ctf in enumerate(ctf_values):
                    r0 = start + 2 + j
                    for k in range(6):
                        append_raw(panel, "input_output_off", ctf, 0.0, k + 1, values[r0][1 + k], r0, 1 + k, "left_off")
                        append_raw(panel, "input_output_on", ctf, 1000.0, k + 1, values[r0][13 + k], r0, 13 + k, "left_on")
                append_dose_matrix(
                    panel, start + 2, range(start + 3, start + 11), 19,
                    [20 + group_width * j for j in range(6)], [group_width] * 6, ctf_values,
                )
            else:
                ctf_values = [clean_number(values[start + 2 + j][0]) for j in range(6)]
                for j, ctf in enumerate(ctf_values):
                    r0 = start + 2 + j
                    for k in range(6):
                        append_raw(panel, "input_output_off", ctf, 0.0, k + 1, values[r0][1 + k], r0, 1 + k, "left_off")
                        append_raw(panel, "input_output_on", ctf, 1000.0, k + 1, values[r0][13 + k], r0, 13 + k, "left_on")
                append_ordinal_labeled_dose_matrix(
                    panel, start + 2, range(start + 3, start + 11), 19,
                    [20 + 8 * j for j in range(6)], [8] * 6, ctf_values,
                )
        elif panel.source_kind == "LBD":
            ctf_values = [clean_number(values[start + 2 + j][0]) for j in range(6)]
            max_dose = clean_number(values[start + 8][13])
            for j, ctf in enumerate(ctf_values):
                r0 = start + 2 + j
                for k in range(6):
                    append_raw(panel, "input_output_off", ctf, 0.0, k + 1, values[r0][1 + k], r0, 1 + k, "left_off")
                    append_raw(panel, "input_output_on", ctf, max_dose, k + 1, values[r0][7 + k], r0, 7 + k, "left_on")
            if panel.panel_id == "SN9-P5-D":
                # GR uses two batch-specific actual-input headers per nominal
                # input, each followed by its second replicate.  Merged nominal
                # labels make the later groups begin two columns to the right of
                # the standard six-column LBD layout.
                append_dose_matrix(
                    panel, start, range(start + 1, start + 9), 13,
                    [14, 22, 28, 34, 40, 46], [4] * 6, ctf_values,
                )
            else:
                dose_header_row = None
                for candidate in (start, start - 1, start + 1):
                    if all(parse_cell(values[candidate][14 + 6 * j])[0] is not None for j in range(6)):
                        dose_header_row = candidate
                        break
                if dose_header_row is None:
                    raise ValueError(f"No six-input dose-response header found for {panel.panel_id} near row {panel.block_row}")
                append_dose_matrix(
                    panel, dose_header_row, range(start + 1, start + 9), 13,
                    [14 + 6 * j for j in range(6)], [6] * 6, ctf_values,
                )
        elif panel.source_kind == "BJAMUT_SPECIAL":
            for j, r0 in enumerate(range(275, 281)):
                ctf = clean_number(values[r0][0])
                for k in range(9):
                    append_raw(panel, "input_output_off", ctf, 0.0, k + 1, values[r0][1 + k], r0, 1 + k, "left_off_day")
                    append_raw(panel, "input_output_on", ctf, 1000.0, k + 1, values[r0][10 + k], r0, 10 + k, "left_on_day")
            starts = [21, 30, 39, 48, 57, 66]
            nominal_inputs = [clean_number(values[275 + j][0]) for j in range(6)]
            append_actual_labeled_dose_matrix(
                panel, 272, 273, range(274, 282), 20,
                starts, [9] * 6, nominal_inputs, batch_kind="Day",
            )
        elif panel.source_kind == "CAR_SPECIAL":
            for j, r0 in enumerate(range(287, 293)):
                ctf = clean_number(values[r0][0])
                for k in range(9):
                    append_raw(panel, "input_output_off", ctf, 0.0, k + 1, values[r0][1 + k], r0, 1 + k, "left_off_run")
                    append_raw(panel, "input_output_on", ctf, 10.0, k + 1, values[r0][10 + k], r0, 10 + k, "left_on_run")
            starts = [21, 30, 42, 48, 57, 66]
            widths = [9, 12, 6, 9, 9, 9]
            nominal_inputs = [clean_number(values[287 + j][0]) for j in range(6)]
            append_actual_labeled_dose_matrix(
                panel, 286, 287, range(288, 296), 20,
                starts, widths, nominal_inputs, batch_kind="Run",
            )
        else:
            raise ValueError(panel.source_kind)


    return raw_rows
