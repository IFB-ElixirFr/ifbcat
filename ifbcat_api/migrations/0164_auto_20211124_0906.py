# Generated by Django 3.2.5 on 2021-11-24 09:06

from django.db import migrations, models
from django.db.models import Min, Max, F


def migrate_opening_closing(apps, schema_editor):
    Event = apps.get_model("ifbcat_api", "Event")
    result = Event.objects.annotate(min=Min('dates__dateStart'), max=Max('dates__dateEnd'))
    for e in result:
        e.start_date = e.min
        e.end_date = e.max
        e.save()


class Migration(migrations.Migration):
    dependencies = [
        ('ifbcat_api', '0163_auto_20211006_0845'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='end_date',
            field=models.DateField(blank=True, help_text='Set the end date of the event', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='start_date',
            field=models.DateField(blank='True', help_text='Set the start date of the event', null=True),
        ),
        migrations.RunPython(code=migrate_opening_closing, reverse_code=migrations.RunPython.noop),
    ]
