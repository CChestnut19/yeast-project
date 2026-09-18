"""Compute predictions and log10 R2 for the twelve Note 11 panels."""
from yeast.metrics import regression_metrics
from yeast.reporting import write_results, validate_results
from .data import read_data, DEFAULT_DATA, DEFAULT_OUTPUT
from .model import PANELS, predicted_rpu, model_settings


def calculate_predictions(rows):
    return [{**r, 'prediction_rpu': predicted_rpu(r['panel'], r['condition'], r['x_value_uM'], r['series_value_uM'])} for r in rows]


def summarize(rows):
    predicted = calculate_predictions(rows)
    return {panel: regression_metrics(
        [r['mean_RPU'] for r in predicted if r['panel'] == panel],
        [r['prediction_rpu'] for r in predicted if r['panel'] == panel]) for panel in PANELS}


def run(data_path=DEFAULT_DATA, output_dir=DEFAULT_OUTPUT):
    rows = read_data(data_path)
    predicted, metrics = calculate_predictions(rows), summarize(rows)
    write_results(output_dir, predicted, metrics, data_path, model_settings())
    result = validate_results(output_dir, predicted, metrics, data_path, model_settings())
    return result


def validate(data_path, output_dir):
    rows = read_data(data_path)
    return validate_results(output_dir, calculate_predictions(rows), summarize(rows), data_path, model_settings())
