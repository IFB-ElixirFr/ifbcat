# Generated by Django 3.2.12 on 2022-11-29 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0188_auto_20220628_0924'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='postalCode',
            field=models.CharField(blank=True, help_text='Postal Code of the city, example: 29680', max_length=5),
        ),
        migrations.AddField(
            model_name='event',
            name='streetAddress',
            field=models.CharField(blank=True, help_text='The street name and number of the address.', max_length=255),
        ),
        migrations.AddField(
            model_name='team',
            name='postalCode',
            field=models.CharField(blank=True, help_text='Postal code of the city, example: 29680', max_length=5),
        ),
        migrations.AlterField(
            model_name='event',
            name='venue',
            field=models.TextField(blank=True, help_text='Information to access to the event, such as the floor, the building name, the door to use, ...'),
        ),
    ]
