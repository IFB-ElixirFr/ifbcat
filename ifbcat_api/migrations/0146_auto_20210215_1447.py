# Generated by Django 3.0.11 on 2021-02-15 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0145_auto_20210215_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='organisedByTeams',
            field=models.ManyToManyField(blank=True, help_text='A Team that is organizing the event.', related_name='organized_events', to='ifbcat_api.Team'),
        ),
    ]
