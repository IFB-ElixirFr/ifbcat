# Generated by Django 3.0.7 on 2020-10-21 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0125_auto_20201021_1223'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tool',
            old_name='operatingSystem',
            new_name='operating_system',
        ),
    ]
