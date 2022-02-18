# Generated by Django 3.2.5 on 2022-02-18 16:32

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0176_alter_team_expertise'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='hoursHandsOn',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Total time (hours) of hands-on / practical work.', null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='event',
            name='hoursPresentations',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Total time (hours) of presented training material.', null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='event',
            name='hoursTotal',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Total time investment (hours) of the training event, including recommended prework.', null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]