from django.core.management import BaseCommand

from ifbcat_api import models
from ifbcat_api.admin import KeywordAdmin


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Clean keywords, split by comma and semi-comma
        ka = KeywordAdmin(model=models.Keyword, admin_site=None)
        ka.split_by_comma_and_remove(None, models.Keyword.objects.all())
        ka.merge_other_where_only_case_differs(None, models.Keyword.objects.all())
        models.Keyword.objects.filter(keyword="").delete()

        # End
