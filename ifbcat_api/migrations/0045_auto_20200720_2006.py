# Generated by Django 3.0 on 2020-07-20 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0044_auto_20200720_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='community',
            name='organisations',
            field=models.ManyToManyField(blank=True, help_text='An organisation to which the community is affiliated.', null=True, related_name='communities', to='ifbcat_api.Organisation'),
        ),
    ]