# Generated by Django 3.2.5 on 2022-02-18 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0178_auto_20220218_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='name',
            field=models.CharField(help_text="Name of the community, e.g. 'Galaxy'.", max_length=255, unique=True),
        ),
    ]
