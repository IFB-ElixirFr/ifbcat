# Generated by Django 3.0 on 2020-08-25 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0084_auto_20200825_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingmaterial',
            name='providedBy',
            field=models.ManyToManyField(blank=True, help_text='The bioinformatics team that provides the training material.', related_name='trainingMaterials', to='ifbcat_api.BioinformaticsTeam'),
        ),
    ]