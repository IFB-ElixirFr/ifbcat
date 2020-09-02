# Generated by Django 3.0 on 2020-09-02 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcatsandbox_api', '0094_auto_20200827_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='orgid',
            field=models.CharField(help_text='Organisation ID (GRID or ROR ID) of the organisation.', max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='trainingmaterial',
            name='doi',
            field=models.CharField(help_text='Unique identier (DOI) of the training material, e.g. a Zenodo DOI.', max_length=255, null=True, unique=True),
        ),
    ]
