# Generated by Django 3.0 on 2020-08-19 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcatsandbox_api', '0074_computingfacility_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='computingfacility',
            name='providedBy',
            field=models.ForeignKey(help_text='The bioinformatics team that provides the computing facility.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='computingFacilityProvidedBy', to='ifbcatsandbox_api.BioinformaticsTeam'),
        ),
        migrations.AlterField(
            model_name='computingfacility',
            name='team',
            field=models.ForeignKey(help_text='The team which is maintaining the computing facility.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='computingFacilityTeam', to='ifbcatsandbox_api.Team'),
        ),
    ]