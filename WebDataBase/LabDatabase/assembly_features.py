"""Serialize normalized assembly annotations as 1-based closed intervals."""
from .feature_records import normalized_record, feature_rows


def assembly_feature_payload(record):
    return feature_rows(normalized_record(record))
