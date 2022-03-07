from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db.models import Q

from ifbcat_api import models
from ifbcat_api.admin import KeywordAdmin


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Clean keywords, split by comma and semi-comma
        ka = KeywordAdmin(model=models.Keyword, admin_site=None)
        ka.split_by_comma_and_remove(None, models.Keyword.objects.all())
        ka.merge_other_where_only_case_differs(None, models.Keyword.objects.all())
        models.Keyword.objects.filter(keyword="").delete()

        # Remove nan of users
        get_user_model().objects.filter(homepage="nan").update(homepage=None)

        # Default description of teams
        models.Team.objects.filter(Q(description__isnull=True) | Q(description="")).update(
            description="To be completed..."
        )

        # End
