# Generated by Django 3.0 on 2020-07-20 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcatsandbox_api', '0042_auto_20200720_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='dates',
            field=models.ManyToManyField(blank=True, help_text='Date(s) and optional time periods on which the event takes place.', null=True, related_name='events', to='ifbcatsandbox_api.EventDate'),
        ),
    ]