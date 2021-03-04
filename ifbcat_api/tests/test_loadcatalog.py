import logging

from django.core import management

from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.team import Team
from ifbcat_api.model.userProfile import UserProfile
from ifbcat_api.tests.test_with_importdata import EnsureImportDataAreHere

logger = logging.getLogger(__name__)


class LoadCatalogTestCase(EnsureImportDataAreHere):
    def test_import_in_db(self):
        management.call_command('load_catalog')
        self.assertEqual(
            UserProfile.objects.count(),
            541,
        )
        self.assertEqual(
            Team.objects.count(),
            32,
        )
        self.assertEqual(
            Organisation.objects.count(),
            59,
        )
