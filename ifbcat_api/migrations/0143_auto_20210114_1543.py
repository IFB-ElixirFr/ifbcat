# Generated by Django 3.0.11 on 2021-01-14 15:43

from django.db import migrations, models
import ifbcat_api.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0142_auto_20210114_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='orgid',
            field=models.CharField(blank=True, help_text='Organisation ID (GRID or ROR ID)', max_length=255, null=True, unique=True, validators=[ifbcat_api.validators.validate_grid_or_ror_id]),
        ),
        migrations.AlterField(
            model_name='team',
            name='orgid',
            field=models.CharField(blank=True, help_text='Organisation ID (GRID or ROR ID)', max_length=255, null=True, unique=True, validators=[ifbcat_api.validators.validate_grid_or_ror_id]),
        ),
    ]