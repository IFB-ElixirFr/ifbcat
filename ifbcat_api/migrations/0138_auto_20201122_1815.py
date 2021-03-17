# Generated by Django 3.0.7 on 2020-11-22 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0137_delete_newsitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='tool',
            name='downloads',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='tool',
            name='team',
            field=models.ManyToManyField(blank=True, help_text='Team developping the tool.', related_name='ToolsTeams', to='ifbcat_api.Team'),
        ),
    ]
