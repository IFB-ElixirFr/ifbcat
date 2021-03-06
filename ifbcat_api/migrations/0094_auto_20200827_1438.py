# Generated by Django 3.0 on 2020-08-27 14:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0093_delete_eventtopic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(help_text='Name of the project.', max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9 \\-_~]+$', 'Should only contains char such as ^[a-zA-Z0-9\\-_~]')]),
        ),
    ]
