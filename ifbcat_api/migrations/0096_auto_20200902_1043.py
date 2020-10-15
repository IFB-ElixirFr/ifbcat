# Generated by Django 3.0 on 2020-09-02 10:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0095_auto_20200902_1009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicesubmission',
            name='year',
            field=models.PositiveSmallIntegerField(blank=True, help_text='The year when the service was submitted for consideration of incluson in the French SDP.', null=True, validators=[django.core.validators.MinValueValidator(2020), django.core.validators.MaxValueValidator(2050)]),
        ),
    ]