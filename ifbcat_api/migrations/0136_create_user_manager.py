# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.management import create_permissions
from django.db import migrations

from ifbcat_api import business_logic


def fix_permissions(apps, schema_editor):
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, verbosity=0)
        app_config.models_module = None


def migration_code(apps, schema_editor):
    business_logic.init_business_logic()


class Migration(migrations.Migration):
    dependencies = [
        ('ifbcat_api', '0135_auto_20201116_1752'),
    ]

    operations = [
        migrations.RunPython(fix_permissions, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(migration_code, reverse_code=migrations.RunPython.noop),
    ]
