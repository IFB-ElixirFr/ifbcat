# Generated by Django 3.2.12 on 2022-03-10 14:31

from django.conf import settings
from django.db import migrations, models


def migrate(apps, schema_editor):
    for o in apps.get_model("ifbcat_api", "Event").objects.filter(trainers_old__isnull=False).distinct():
        for t in o.trainers_old.all():
            user = t.trainerId
            if user is None:
                names = t.trainerName.split(" ")
                assert len(names) == 2
                user, _ = apps.get_model("ifbcat_api", "UserProfile").objects.get_or_create(
                    email=t.trainerEmail,
                    defaults=dict(firstname=names[0], lastname=names[1]),
                )
            o.trainers.add(user)
        # o.trainers.add(o.contactId)


def migrate_back(apps, schema_editor):
    for o in apps.get_model("ifbcat_api", "Event").objects.filter(trainers__isnull=False).distinct():
        for t in o.trainers.all():
            trainer, _ = apps.get_model("ifbcat_api", "Trainer").objects.get_or_create(
                trainerEmail=t.email,
                defaults=dict(trainerName=f'{t.firstname} {t.lastname}', trainerId=t),
            )
            o.trainers_old.add(trainer)


def migrate_contacts(apps, schema_editor):
    for o in apps.get_model("ifbcat_api", "Event").objects.filter(contactEmail__isnull=False).exclude(contactEmail=""):
        o.contacts.add(apps.get_model("ifbcat_api", "UserProfile").objects.get(email=o.contactEmail))


def migrate_back_contacts(apps, schema_editor):
    for o in apps.get_model("ifbcat_api", "Event").objects.all():
        for c in o.contacts.all():
            o.contactEmail = c.email
            o.contactName = f'{c.firstname} {c.lastname}'


class Migration(migrations.Migration):
    dependencies = [
        ('ifbcat_api', '0181_auto_20220307_0951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='contactEmail',
            field=models.EmailField(
                default='', help_text='Email of person to contact about the event.', max_length=254
            ),
        ),
        migrations.AlterField(
            model_name='event',
            name='contactName',
            field=models.CharField(default='', help_text='Name of person to contact about the event.', max_length=255),
        ),
        migrations.AlterField(
            model_name='training',
            name='contactEmail',
            field=models.EmailField(
                default='', help_text='Email of person to contact about the event.', max_length=254
            ),
        ),
        migrations.AlterField(
            model_name='training',
            name='contactName',
            field=models.CharField(default='', help_text='Name of person to contact about the event.', max_length=255),
        ),
        migrations.RenameField(
            model_name='event',
            old_name='trainers',
            new_name='trainers_old',
        ),
        migrations.AddField(
            model_name='event',
            name='trainers',
            field=models.ManyToManyField(
                blank=True,
                help_text='Details of people who are providing training at the event.',
                related_name='eventTrainers',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(code=migrate, reverse_code=migrate_back),
        migrations.RemoveField(
            model_name='event',
            name='trainers_old',
        ),
        migrations.DeleteModel(
            name='Trainer',
        ),
        migrations.AddField(
            model_name='event',
            name='contacts',
            field=models.ManyToManyField(
                blank=True,
                help_text='Person(s) to contact about the event.',
                related_name='_ifbcat_api_event_contacts_+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='training',
            name='contacts',
            field=models.ManyToManyField(
                blank=True,
                help_text='Person(s) to contact about the event.',
                related_name='_ifbcat_api_training_contacts_+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(code=migrate_contacts, reverse_code=migrate_back_contacts),
        migrations.RemoveField(
            model_name='event',
            name='contactEmail',
        ),
        migrations.RemoveField(
            model_name='event',
            name='contactName',
        ),
        migrations.RemoveField(
            model_name='training',
            name='contactEmail',
        ),
        migrations.RemoveField(
            model_name='training',
            name='contactName',
        ),
    ]
