# Generated by Django 3.2.5 on 2021-11-30 16:40

from django.db import migrations, models
import ifbcat_api.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0164_auto_20211124_0906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='dates',
        ),
    ]
