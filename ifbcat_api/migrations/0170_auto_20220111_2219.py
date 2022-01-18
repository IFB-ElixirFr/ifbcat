# Generated by Django 3.2.5 on 2022-01-11 22:19

from django.db import migrations, models
from django.db.models import Case, When, Value, CharField


def migrate_onlineonly_coursemode(apps, schema_editor):
    Event = apps.get_model("ifbcat_api", "Event")
    result = Event.objects.annotate(
        is_online=Case(
            When(onlineOnly=True,
                 then=Value("Online")),
            When(onlineOnly=False,
                 then=Value("Onsite")),
            default=Value(""),
            output_field=CharField()
        )
    )
    for e in result:
        e.courseMode = e.is_online
        e.save()


class Migration(migrations.Migration):
    dependencies = [
        ('ifbcat_api', '0169_alter_topic_uri'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='courseMode',
            field=models.CharField(choices=[('Online', 'Online'), ('Onsite', 'Onsite'), ('Blended', 'Blended')],
                                   default=None, help_text='Select the mode for this event', max_length=10,
                                   null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='is_draft',
            field=models.BooleanField(default=False, help_text="Mention whether it's a draft."),
        ),
        migrations.AddField(
            model_name='training',
            name='is_draft',
            field=models.BooleanField(default=False, help_text="Mention whether it's a draft."),
        ),
        migrations.RunPython(code=migrate_onlineonly_coursemode, reverse_code=migrations.RunPython.noop),
    ]