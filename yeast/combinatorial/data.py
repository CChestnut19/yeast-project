"""Read the supplied Note 11 cell means without pooling or re-fitting."""
from pathlib import Path
from yeast.reporting import number, read_records
from .model import PANELS

DEFAULT_DATA = Path(__file__).resolve().parent / 'data/Supplementary_Note_11_plot_data.csv'
DEFAULT_RESOURCES = Path(__file__).resolve().parent / 'resources'
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / 'Output/combinatorial'
COLUMNS = ('panel', 'condition', 'x_value_uM', 'series_value_uM', 'mean_RPU', 'sample_SD_RPU')


def read_plot_data(path):
    rows, keys = [], set()
    for index, source in enumerate(read_records(path, COLUMNS), 2):
        panel = source['panel']
        row = {'panel': panel}
        for column in COLUMNS[1:]:
            row[column] = number(source[column], f'CSV row {index}, {column}',
                                 positive=column in ('mean_RPU', 'condition'), integer=column == 'condition')
        if panel not in PANELS or row['condition'] != int(panel[1]):
            raise ValueError(f'CSV row {index}: invalid panel/condition pair')
        key = (panel, row['x_value_uM'], row['series_value_uM'])
        if key in keys:
            raise ValueError(f'CSV row {index}: duplicate panel/dose/series mean')
        keys.add(key)
        rows.append(row)
    if {row['panel'] for row in rows} != set(PANELS):
        raise ValueError('Expected observations for all 12 Note 11 panels')
    return rows
