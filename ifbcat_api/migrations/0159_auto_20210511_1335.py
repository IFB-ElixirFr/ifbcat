# Generated by Django 3.0.14 on 2021-05-11 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0158_auto_20210511_1049'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='market',
        ),
        migrations.AddField(
            model_name='event',
            name='geographical_range',
            field=models.CharField(blank=True, choices=[('Local', 'Local or regional'), ('National', 'National'), ('International', 'International')], help_text='Geographical area which is the focus of event marketing efforts.', max_length=255),
        ),
        migrations.AddField(
            model_name='training',
            name='homepage',
            field=models.URLField(blank=True, help_text='URL of event homepage.', max_length=255),
        ),
        migrations.AlterField(
            model_name='event',
            name='homepage',
            field=models.URLField(blank=True, help_text='URL of event homepage.', max_length=255),
        ),
    ]
