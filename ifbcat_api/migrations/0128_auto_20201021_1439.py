# Generated by Django 3.0.7 on 2020-10-21 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0127_auto_20201021_1425'),
    ]

    operations = [
        migrations.RenameField(
            model_name='toolcredit',
            old_name='typeRole',
            new_name='type_role',
        ),
    ]
