import uuid
from django.db import migrations, models
import django.db.models.deletion

def upgrade_feature_tables(apps, schema_editor):
    connection = schema_editor.connection
    tables = {name.lower() for name in connection.introspection.table_names()}
    added = ('strand', 'feature_group', 'segment_order', 'location_operator',
             'coordinate_system', 'feature_metadata')
    for name in ('Backbonefeaturetable', 'Partfeaturetable', 'Plasmidfeaturetable'):
        model = apps.get_model('WebDatabase', name)
        if model._meta.db_table.lower() not in tables:
            schema_editor.create_model(model)
            continue
        with connection.cursor() as cursor:
            columns = {c.name for c in connection.introspection.get_table_description(cursor, model._meta.db_table)}
        for name in added:
            field = model._meta.get_field(name)
            if field.column not in columns:
                schema_editor.add_field(model, field)


class Migration(migrations.Migration):
    dependencies = [('WebDatabase', '0003_backbonetable_dbdtable_lbddimertable_lbdnrtable_and_more')]
    operations = [
        migrations.SeparateDatabaseAndState(state_operations=[
            migrations.CreateModel(name='Backbonefeaturetable', fields=[
                ('bfif', models.AutoField(primary_key=True, serialize=False)),
                ('backboneid', models.ForeignKey(to='WebDatabase.backbonetable', on_delete=django.db.models.deletion.CASCADE, db_column='backboneid')),
                ('feature_start', models.IntegerField()), ('feature_end', models.IntegerField()),
                ('feature_type', models.CharField(max_length=50)), ('feature_label', models.CharField(max_length=50)),
                ('feature_color', models.CharField(max_length=50)), ('feature_apeinfo', models.CharField(max_length=50)),
                ('strand', models.SmallIntegerField(null=True, blank=True)),
                ('feature_group', models.CharField(max_length=64, null=True, blank=True, db_index=True)),
                ('segment_order', models.PositiveIntegerField(default=0)),
                ('location_operator', models.CharField(max_length=10, default='', blank=True)),
                ('coordinate_system', models.CharField(max_length=24, default='legacy_unknown')),
                ('feature_metadata', models.JSONField(default=dict, blank=True)),
            ], options={'db_table': 'BackboneFeatureTable', 'managed': True}),
            migrations.CreateModel(name='Partfeaturetable', fields=[
                ('pfid', models.AutoField(primary_key=True, serialize=False)),
                ('partid', models.ForeignKey(to='WebDatabase.parttable', on_delete=django.db.models.deletion.CASCADE, db_column='partid')),
                ('feature_start', models.IntegerField()), ('feature_end', models.IntegerField()),
                ('feature_type', models.CharField(max_length=50)), ('feature_label', models.CharField(max_length=50)),
                ('feature_color', models.CharField(max_length=50)), ('feature_apeinfo', models.CharField(max_length=50)),
                ('strand', models.SmallIntegerField(null=True, blank=True)),
                ('feature_group', models.CharField(max_length=64, null=True, blank=True, db_index=True)),
                ('segment_order', models.PositiveIntegerField(default=0)),
                ('location_operator', models.CharField(max_length=10, default='', blank=True)),
                ('coordinate_system', models.CharField(max_length=24, default='legacy_unknown')),
                ('feature_metadata', models.JSONField(default=dict, blank=True)),
            ], options={'db_table': 'PartFeatureTable', 'managed': True}),
            migrations.CreateModel(name='Plasmidfeaturetable', fields=[
                ('pfid', models.AutoField(primary_key=True, serialize=False)),
                ('plasmidid', models.ForeignKey(to='WebDatabase.plasmidneed', on_delete=django.db.models.deletion.CASCADE, db_column='plasmidid')),
                ('feature_start', models.IntegerField()), ('feature_end', models.IntegerField()),
                ('feature_type', models.CharField(max_length=50)), ('feature_label', models.CharField(max_length=50)),
                ('feature_color', models.CharField(max_length=50)), ('feature_apeinfo', models.CharField(max_length=50)),
                ('strand', models.SmallIntegerField(null=True, blank=True)),
                ('feature_group', models.CharField(max_length=64, null=True, blank=True, db_index=True)),
                ('segment_order', models.PositiveIntegerField(default=0)),
                ('location_operator', models.CharField(max_length=10, default='', blank=True)),
                ('coordinate_system', models.CharField(max_length=24, default='legacy_unknown')),
                ('feature_metadata', models.JSONField(default=dict, blank=True)),
            ], options={'db_table': 'PlasmidFeatureTable', 'managed': True}),
        ]),
        migrations.RunPython(upgrade_feature_tables, migrations.RunPython.noop, atomic=False),
        migrations.CreateModel(name='AssemblyResultVersion', fields=[
            ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
            ('task_id', models.CharField(max_length=64, db_index=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('record', models.JSONField()), ('genbank', models.TextField()),
            ('sequence_digest', models.CharField(max_length=64)),
            ('annotation_digest', models.CharField(max_length=64)),
            ('input_sources', models.JSONField(default=list)),
            ('stored_rows_digest', models.CharField(max_length=64, default='')),
            ('revision_kind', models.CharField(max_length=24, default='assembly')),
            ('plasmid', models.ForeignKey(to='WebDatabase.plasmidneed', on_delete=django.db.models.deletion.CASCADE, related_name='assembly_versions')),
        ], options={'db_table': 'assembly_result_version', 'ordering': ['-created_at']}),
        migrations.CreateModel(name='AssemblyTask', fields=[
            ('id', models.CharField(primary_key=True, max_length=64, serialize=False)),
            ('request_key', models.CharField(max_length=64, unique=True, null=True)),
            ('owner_id', models.CharField(max_length=64)), ('target', models.CharField(max_length=500)),
            ('execution_mode', models.CharField(max_length=32, default='assemble')),
            ('state', models.JSONField(default=dict)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
        ], options={'db_table': 'assembly_task'}),
    ]
