# Generated by Django 3.2.12 on 2022-02-28 13:41

from django.db import migrations, models
from django.db.models import Case, When, Value


def migrate(apps, schema_editor):
    for klass in [apps.get_model("ifbcat_api", "Event"), apps.get_model("ifbcat_api", "Training")]:
        klass.objects.update(
            openTo=Case(
                When(accessibility='Public', then=Value('Everyone')),
                # When(accessibility='Private', then=Value('Internal personnel')),
                default=Value('Internal personnel'),
            )
        )


def migrate_back(apps, schema_editor):
    for klass in [apps.get_model("ifbcat_api", "Event"), apps.get_model("ifbcat_api", "Training")]:
        klass.objects.update(
            accessibility=Case(
                When(openTo='Everyone', then=Value('Public')),
                # When(openTo='Internal personnel', then=Value('Private')),
                default=Value('Private'),
            )
        )


class Migration(migrations.Migration):
    dependencies = [
        ('ifbcat_api', '0179_alter_community_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='accessibility',
            field=models.CharField(
                choices=[('Public', 'Public'), ('Private', 'Private')],
                default='',
                help_text='Whether the event is public or private.',
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name='training',
            name='accessibility',
            field=models.CharField(
                choices=[('Public', 'Public'), ('Private', 'Private')],
                default='',
                help_text='Whether the event is public or private.',
                max_length=255,
            ),
        ),
        migrations.RenameField(
            model_name='event',
            old_name='accessibilityNote',
            new_name='accessConditions',
        ),
        migrations.RenameField(
            model_name='training',
            old_name='accessibilityNote',
            new_name='accessConditions',
        ),
        migrations.AlterField(
            model_name='event',
            name='accessConditions',
            field=models.TextField(
                blank=True,
                help_text='Comment on how one can access. Mandatory if not open to everyone',
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='training',
            name='accessConditions',
            field=models.TextField(
                blank=True,
                help_text='Comment on how one can access. Mandatory if not open to everyone',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='openTo',
            field=models.CharField(
                choices=[('Everyone', 'Everyone'), ('Internal personnel', 'Internal personnel'), ('Others', 'Others')],
                default='Others',
                help_text='Whether the event is for everyone, internal personnel or others.',
                max_length=255,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='training',
            name='openTo',
            field=models.CharField(
                choices=[('Everyone', 'Everyone'), ('Internal personnel', 'Internal personnel'), ('Others', 'Others')],
                default='Others',
                help_text='Whether the event is for everyone, internal personnel or others.',
                max_length=255,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(code=migrate, reverse_code=migrate_back),
        migrations.RemoveField(
            model_name='event',
            name='accessibility',
        ),
        migrations.RemoveField(
            model_name='training',
            name='accessibility',
        ),
    ]
