# Generated by Django 3.2.12 on 2024-04-18 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0189_auto_20221129_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='ifbMembership',
            field=models.CharField(
                choices=[
                    ('Associated Team', 'Associated Team'),
                    ('Contributing platform', 'Contributing platform'),
                    ('Coordinating platform', 'Coordinating platform'),
                    ('Member platform', 'Member platform'),
                    ('None', 'None'),
                ],
                default='None',
                help_text='Type of membership the bioinformatics team has to IFB.',
                max_length=255,
            ),
        ),
    ]
