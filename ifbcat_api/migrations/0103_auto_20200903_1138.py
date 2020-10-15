# Generated by Django 3.0 on 2020-09-03 11:38

from django.db import migrations, models
import ifbcat_api.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0102_auto_20200903_1056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bioinformaticsteam',
            name='orgid',
            field=models.CharField(help_text='Organisation ID (GRID or ROR ID) of the team.', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_grid_or_ror_id]),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='orgid',
            field=models.CharField(help_text='Organisation ID (GRID or ROR ID) of the organisation.', max_length=255, null=True, unique=True, validators=[ifbcat_api.validators.validate_grid_or_ror_id]),
        ),
        migrations.AlterField(
            model_name='topic',
            name='topic',
            field=models.CharField(help_text='URI of EDAM Topic term describing scope or expertise.', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_edam_topic]),
        ),
        migrations.AlterField(
            model_name='trainingmaterial',
            name='dateCreation',
            field=models.DateField(blank=True, help_text='Date when the training material was created.'),
        ),
        migrations.AlterField(
            model_name='trainingmaterial',
            name='dateUpdate',
            field=models.DateField(blank=True, help_text='Date when the training material was updated.'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='orcidid',
            field=models.CharField(blank=True, help_text='ORCID ID of a person (IFB catalogue user).', max_length=255, null=True, unique=True, validators=[ifbcat_api.validators.validate_orcid]),
        ),
    ]