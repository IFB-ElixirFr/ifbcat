# Generated by Django 3.2.12 on 2022-06-28 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0187_auto_20220602_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='lat',
            field=models.DecimalField(decimal_places=6, default=None, max_digits=9, null=True, verbose_name='Latitude'),
        ),
        migrations.AddField(
            model_name='team',
            name='lng',
            field=models.DecimalField(decimal_places=6, default=None, max_digits=9, null=True, verbose_name='Longitude'),
        ),
    ]
