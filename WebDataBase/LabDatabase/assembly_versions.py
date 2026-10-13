"""Immutable assembly snapshots and fresh input generation (no name caches)."""
from copy import deepcopy
from django.db import transaction
from .feature_records import (digest, feature_rows, record_data, record_from_data,
                              record_from_rows, normalized_record, genbank_text)


def source_models(kind):
    from WebDatabase.models import (Parttable, Backbonetable, Plasmidneed,
        Partfeaturetable, Backbonefeaturetable, Plasmidfeaturetable)
    return {'part': (Parttable, Partfeaturetable, 'partid', 'level0sequence'),
            'backbone': (Backbonetable, Backbonefeaturetable, 'backboneid', 'sequence'),
            'plasmid': (Plasmidneed, Plasmidfeaturetable, 'plasmidid', 'sequenceconfirm')}[kind]


def stored_rows(kind, ident):
    _, model, key, _ = source_models(kind)
    fields = ['feature_start', 'feature_end', 'strand', 'feature_group', 'segment_order',
              'location_operator', 'coordinate_system', 'feature_type', 'feature_label',
              'feature_color', 'feature_apeinfo', 'feature_metadata']
    return list(model.objects.filter(**{key: ident}).order_by(model._meta.pk.name).values(*fields))


def source_stamp(kind, ident):
    model, _, _, sequence_field = source_models(kind)
    obj = model.objects.get(pk=ident)
    sequence = ''.join((getattr(obj, sequence_field) or '').split())
    rows = stored_rows(kind, ident)
    return {'type': kind, 'id': ident, 'name': obj.name,
            'sequence_digest': digest(sequence.upper()), 'annotation_digest': digest(rows)}


def source_record(kind, ident):
    from WebDatabase.models import AssemblyResultVersion
    model, _, _, sequence_field = source_models(kind)
    obj = model.objects.get(pk=ident)
    sequence = ''.join((getattr(obj, sequence_field) or '').split())
    if not sequence:
        raise ValueError('%s %s has no sequence' % (kind, obj.name))
    rows = stored_rows(kind, ident)
    if kind == 'plasmid':
        version = AssemblyResultVersion.objects.filter(plasmid_id=ident).first()
        if version:
            if version.sequence_digest != digest(sequence.upper()):
                raise ValueError('Sequence changed since assembly; reassemble or explicitly upload a new map')
            if version.stored_rows_digest != digest(rows):
                raise ValueError('Annotations changed since assembly; publish an annotation revision or reassemble')
            return record_from_data(version.record)
    return record_from_rows(sequence, rows, name=obj.name)


def attach_source(record, kind, ident, name, level=None):
    """Tag existing annotations without adding a full-length source feature."""
    stamp = source_stamp(kind, ident)
    revision = digest(stamp)
    for feature in record.features:
        feature.qualifiers.setdefault('source_type', [kind])
        feature.qualifiers.setdefault('source_id', [str(ident)])
        feature.qualifiers.setdefault('source_revision', [revision])
    return record


@transaction.atomic
def save_version(plasmid_id, task_id, record, sources, revision_kind='assembly'):
    from WebDatabase.models import Plasmidneed, Plasmidfeaturetable, AssemblyResultVersion
    obj = Plasmidneed.objects.select_for_update().get(pk=plasmid_id)
    if ''.join(obj.sequenceconfirm.split()).upper() != str(record.seq).upper():
        raise ValueError('Saved sequence differs from assembly result')
    text = genbank_text(record)
    # Persist the very same rows and snapshot together, not a second annotation pass.
    rows = feature_rows(record)
    Plasmidfeaturetable.objects.filter(plasmidid=obj).delete()
    Plasmidfeaturetable.objects.bulk_create([Plasmidfeaturetable(plasmidid=obj, **r) for r in rows])
    data = record_data(record)
    return AssemblyResultVersion.objects.create(plasmid=obj, task_id=task_id,
        record=data, genbank=text, sequence_digest=digest(str(record.seq).upper()),
        annotation_digest=digest(data['features']), input_sources=sources,
        stored_rows_digest=digest(stored_rows('plasmid', plasmid_id)), revision_kind=revision_kind)


def version_status(version):
    from WebDatabase.models import Parentparttable, Parentbackbonetable, Parentplasmidtable
    changed = []
    if version.revision_kind != 'upload':
        current_parents = set()
        for kind, model, field in [('part', Parentparttable, 'parentpartid_id'),
                                   ('backbone', Parentbackbonetable, 'parentbackboneid_id'),
                                   ('plasmid', Parentplasmidtable, 'parentplasmidid_id')]:
            current_parents.update((kind, ident) for ident in model.objects.filter(
                sonplasmidid_id=version.plasmid_id).values_list(field, flat=True))
        expected = {(s['type'], s['id']) for s in version.input_sources}
        if current_parents != expected:
            changed.append({'reason': 'parent_relationships_changed'})
    obj = version.plasmid
    if digest(''.join(obj.sequenceconfirm.split()).upper()) != version.sequence_digest:
        changed.append({'reason': 'target_sequence_changed'})
    if digest(stored_rows('plasmid', obj.pk)) != version.stored_rows_digest:
        changed.append({'reason': 'target_annotations_changed'})
    for old in version.input_sources:
        try:
            current = source_stamp(old['type'], old['id'])
            if any(current[k] != old[k] for k in ('sequence_digest', 'annotation_digest')):
                changed.append({'type': old['type'], 'id': old['id'], 'reason': 'source_changed'})
        except source_models(old['type'])[0].DoesNotExist:
            changed.append({'type': old['type'], 'id': old['id'], 'reason': 'source_missing'})
    return changed


@transaction.atomic
def refresh_source_labels(plasmid_id):
    """Explicit metadata-only revision; historical task versions stay immutable."""
    from WebDatabase.models import AssemblyResultVersion
    previous = AssemblyResultVersion.objects.filter(plasmid_id=plasmid_id).first()
    if not previous:
        raise ValueError('No authoritative assembly version; reassemble this legacy record')
    if version_status(previous):
        raise ValueError('Source sequence/annotations changed; reassembly is required')
    record = source_record('plasmid', plasmid_id)
    for feature in record.features:
        from .feature_records import first
        if first(feature.qualifiers, 'source_container') != 'true':
            continue
        kind, ident = first(feature.qualifiers, 'source_type'), first(feature.qualifiers, 'source_id')
        model = source_models(kind)[0]
        feature.qualifiers['label'] = [model.objects.get(pk=ident).name]
    sources = [source_stamp(s['type'], s['id']) for s in previous.input_sources]
    import uuid
    return save_version(plasmid_id, 'annotation-' + str(uuid.uuid4()), record, sources, 'annotation')


def verified_version_text(version):
    from .feature_records import read_genbank, semantic_data
    import io
    record = record_from_data(version.record)
    if digest(str(record.seq).upper()) != version.sequence_digest or digest(version.record['features']) != version.annotation_digest:
        raise ValueError('Assembly snapshot integrity check failed')
    try:
        parsed = read_genbank(io.StringIO(version.genbank))
        if semantic_data(parsed) == semantic_data(record):
            return version.genbank
    except (ValueError, TypeError, KeyError):
        pass
    return genbank_text(record)
