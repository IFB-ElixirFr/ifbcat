# Generated by Django 3.0.7 on 2020-10-20 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0123_tool_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tool',
            name='description',
            field=models.CharField(max_length=1000),
        ),
    ]
