# Generated by Django 3.0 on 2020-07-21 10:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0049_auto_20200720_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='user_profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
