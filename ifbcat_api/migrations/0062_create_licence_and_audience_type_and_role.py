# Generated by Django 3.0 on 2020-07-20 19:17

from django.db import migrations, models

from django.utils.translation import gettext_lazy as _


def migration_code_type(apps, schema_editor):
    AudienceType = apps.get_model("ifbcat_api", "AudienceType")

    # translated is here just to be extracted by make_messages if needed
    for key, translated in [
        ('Undergraduate', _('Undergraduate')),
        ('Graduate', _('Graduate')),
        ('Professional (initial)', _('Professional (initial)')),
        ('Professional (continued)', _('Professional (continued)')),
    ]:
        AudienceType.objects.get_or_create(audienceType=key)


def migration_code_role(apps, schema_editor):
    AudienceRole = apps.get_model("ifbcat_api", "AudienceRole")

    # translated is here just to be extracted by make_messages if needed
    for key, translated in [
        ('Researchers', _('Researchers')),
        ('Life scientists', _('Life scientists')),
        ('Computer scientists', _('Computer scientists')),
        ('Biologists', _('Biologists')),
        ('Bioinformaticians', _('Bioinformaticians')),
        ('Programmers', _('Programmers')),
        ('Curators', _('Curators')),
        ('Managers', _('Managers')),
        ('All', _('All')),
    ]:
        AudienceRole.objects.get_or_create(audienceRole=key)

def migration_code_licence(apps, schema_editor):
    TrainingMaterialLicense = apps.get_model("ifbcat_api", "TrainingMaterialLicense")

    # translated is here just to be extracted by make_messages if needed
    for key, translated in [
        ('Test license 1', _('Test license 1')),
        ('Test license 2', _('Test license 2')),
    ]:
        TrainingMaterialLicense.objects.get_or_create(name=key)


class Migration(migrations.Migration):
    dependencies = [
        ('ifbcat_api', '0061_auto_20200723_0940'),
    ]

    operations = [
        migrations.RunPython(migration_code_licence, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(migration_code_type, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(migration_code_role, reverse_code=migrations.RunPython.noop),
    ]
