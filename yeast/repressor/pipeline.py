"""Recompute all Note 10 predictions directly from the supplied observations."""
from pathlib import Path
from yeast.metrics import regression_metrics
from yeast.reporting import read_records, number, write_results, validate_results
from .model import SENSORS, predict, model_settings

DEFAULT_DATA = Path(__file__).resolve().parent / 'data/experiment_data.csv'
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / 'Output/repressor'
COLUMNS = ('sensor', 'tf_input_rpu', 'inducer_um', 'replicate', 'experiment_rpu')


def read_data(path):
    rows, keys = [], set()
    for index, source in enumerate(read_records(path, COLUMNS), 2):
        sensor = source['sensor']
        if sensor not in SENSORS:
            raise ValueError(f'CSV row {index}: unknown sensor {sensor!r}')
        row = {'sensor': sensor}
        for column in COLUMNS[1:]:
            row[column] = number(source[column], f'CSV row {index}, {column}',
                                 positive=column in ('replicate', 'experiment_rpu'), integer=column == 'replicate')
        key = tuple(row[column] for column in COLUMNS[:-1])
        if key in keys:
            raise ValueError(f'CSV row {index}: duplicate sensor/input/dose/replicate')
        keys.add(key)
        rows.append(row)
    if {row['sensor'] for row in rows} != set(SENSORS):
        raise ValueError('Expected observations for all four Note 10 sensors')
    return rows


def calculate_predictions(rows):
    return [{**row, 'prediction_rpu': predict(row['sensor'], row['tf_input_rpu'], row['inducer_um'])} for row in rows]


def summarize(rows):
    def metrics(selected, scale):
        return regression_metrics([r['experiment_rpu'] for r in selected], [r['prediction_rpu'] for r in selected], scale)
    return {scale: {'per_sensor': {sensor: metrics([r for r in rows if r['sensor'] == sensor], scale) for sensor in SENSORS},
                    'pooled': metrics(rows, scale)} for scale in ('raw', 'log10')}


def run(data_path=DEFAULT_DATA, output_dir=DEFAULT_OUTPUT):
    rows = calculate_predictions(read_data(data_path))
    metrics = summarize(rows)
    write_results(output_dir, rows, metrics, data_path, model_settings())
    result = validate_results(output_dir, rows, metrics, data_path, model_settings())
    return result


def validate(data_path, output_dir):
    rows = calculate_predictions(read_data(data_path))
    return validate_results(output_dir, rows, summarize(rows), data_path, model_settings())
