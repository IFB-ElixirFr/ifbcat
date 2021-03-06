# Generated by Django 3.0.7 on 2020-09-29 09:21

from django.db import migrations, models

import ifbcat_api.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0117_pg_unaccent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computingfacility',
            name='name',
            field=models.CharField(help_text='Name of the resource.', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_can_be_looked_up]),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='keyword',
            field=models.CharField(help_text='A keyword (beyond EDAM ontology scope).', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_can_be_looked_up]),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='name',
            field=models.CharField(help_text='Name of the organisation.', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_can_be_looked_up]),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(help_text='Name of the project.', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_can_be_looked_up]),
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(help_text='Name of the service.', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_can_be_looked_up]),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(help_text='Name of the team.', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_can_be_looked_up]),
        ),
        migrations.AlterField(
            model_name='trainingmaterial',
            name='name',
            field=models.CharField(help_text='Name of the resource.', max_length=255, unique=True, validators=[ifbcat_api.validators.validate_can_be_looked_up]),
        ),
    ]
