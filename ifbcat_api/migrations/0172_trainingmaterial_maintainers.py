# Generated by Django 3.2.5 on 2022-01-24 12:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0171_auto_20220124_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingmaterial',
            name='maintainers',
            field=models.ManyToManyField(blank=True, help_text='Maintainer(s) of the training material.', related_name='trainingMaterialMaintainers', to=settings.AUTH_USER_MODEL),
        ),
    ]
