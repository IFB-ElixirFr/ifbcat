# Generated by Django 3.0.11 on 2021-03-03 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0149_auto_20210303_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='organisedByOrganisations',
            field=models.ManyToManyField(blank=True, help_text='An organisation that is organizing the event.', related_name='organized_events', to='ifbcat_api.Organisation'),
        ),
        migrations.AlterField(
            model_name='event',
            name='organisedByTeams',
            field=models.ManyToManyField(blank=True, help_text='A Team that is organizing the event.', related_name='organized_events', to='ifbcat_api.Team'),
        ),
    ]
