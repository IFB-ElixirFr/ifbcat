# Generated by Django 3.2.5 on 2021-10-06 08:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0162_auto_20211004_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='accessibilityNote',
            field=models.TextField(blank=True, help_text='Comment about the audience a private event is open to and tailored for.', null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='leader',
            field=models.ForeignKey(blank=True, help_text='Leader of the team.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teamLeader', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='trainer',
            name='trainerId',
            field=models.ForeignKey(blank=True, help_text='IFB ID of person who is providing training at the training event.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='training',
            name='accessibilityNote',
            field=models.TextField(blank=True, help_text='Comment about the audience a private event is open to and tailored for.', null=True),
        ),
    ]
