# Generated by Django 3.2.5 on 2022-01-04 23:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0169_alter_topic_uri'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tool',
            name='access_condition',
        ),
        migrations.RemoveField(
            model_name='tool',
            name='contact_support',
        ),
        migrations.RemoveField(
            model_name='tool',
            name='keywords',
        ),
        migrations.RemoveField(
            model_name='tool',
            name='logo',
        ),
        migrations.RemoveField(
            model_name='tool',
            name='prerequisites',
        ),
        migrations.RemoveField(
            model_name='tool',
            name='primary',
        ),
    ]