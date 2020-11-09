import logging
import os
from unittest.case import skipIf

from django.core import management

from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.team import Team
from ifbcat_api.tests.test_with_importdata import EnsureImportDataAreHere

logger = logging.getLogger(__name__)


@skipIf(True, "use test_loadcatalog instead, kept as an example")
class LoadBioinfoTeamsTestCase(EnsureImportDataAreHere):
    def test_import_in_db(self):
        management.call_command('load_bioinformatics_teams', os.path.join(self.import_data, "platforms.csv"))
        print("%i Teams #######################################" % Team.objects.count())
        for t in Team.objects.all():
            print(t)
        print("%i Organisation #######################################" % Organisation.objects.count())
        for o in Organisation.objects.all():
            print(o)
