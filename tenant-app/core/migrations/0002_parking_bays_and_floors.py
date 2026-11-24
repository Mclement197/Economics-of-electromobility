from django.db import migrations, models
import django.db.models.deletion


def backfill_reservation_bays(apps, schema_editor):
    Reservation = apps.get_model('core', 'Reservation')
    Charger = apps.get_model('core', 'Charger')
    alias = schema_editor.connection.alias
    for charger_id, bay_id in Charger.objects.using(alias).values_list('id', 'bay_id'):
        Reservation.objects.using(alias).filter(charger_id=charger_id, bay__isnull=True).update(bay_id=bay_id)
    if Reservation.objects.using(alias).filter(bay__isnull=True).exists():
        raise RuntimeError('Cannot migrate reservations without a known parking bay.')


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.AddField(model_name='bay', name='floor', field=models.CharField(default='UG1', max_length=40)),
        migrations.AddField(model_name='bay', name='bookable', field=models.BooleanField(default=True)),
        migrations.RemoveConstraint(model_name='bay', name='unique_bay_position'),
        migrations.AddConstraint(model_name='bay', constraint=models.UniqueConstraint(fields=('property', 'floor', 'row', 'column'), name='unique_bay_floor_position')),
        migrations.AddField(model_name='reservation', name='bay', field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to='core.bay')),
        migrations.RunPython(backfill_reservation_bays, migrations.RunPython.noop),
        migrations.AlterField(model_name='reservation', name='bay', field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to='core.bay')),
        migrations.AlterField(model_name='reservation', name='charger', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reservations', to='core.charger')),
        migrations.AddIndex(model_name='reservation', index=models.Index(fields=['bay', 'status', 'start', 'end'], name='reservation_bay_interval')),
    ]
