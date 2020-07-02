# Generated by Django 3.0 on 2020-07-02 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcatsandbox_api', '0013_auto_20200701_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='accessibility',
            field=models.CharField(blank=True, choices=[('PU', 'Public'), ('PR', 'Private')], help_text='.', max_length=2),
        ),
        migrations.AddField(
            model_name='event',
            name='cost',
            field=models.CharField(blank=True, choices=[('FR', 'Free'), ('FA', 'Free to academics'), ('CO', 'Concessions available')], help_text='Whether the event is public or private.', max_length=2),
        ),
    ]
