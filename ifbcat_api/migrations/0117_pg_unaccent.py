from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('ifbcat_api', '0116_userprofile_expertise'),
    ]

    operations = [
        UnaccentExtension(),
    ]
