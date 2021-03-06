# Generated by Django 3.0 on 2020-07-02 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0014_auto_20200702_0836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='accessibility',
            field=models.CharField(blank=True, choices=[('PU', 'Public'), ('PR', 'Private')], help_text='Whether the event is public or private.', max_length=2),
        ),
        migrations.AlterField(
            model_name='event',
            name='cost',
            field=models.CharField(blank=True, choices=[('FR', 'Free'), ('FA', 'Free to academics'), ('CO', 'Concessions available')], help_text="Monetary cost to attend the event, e.g. 'Free to academics'.", max_length=2),
        ),
    ]
