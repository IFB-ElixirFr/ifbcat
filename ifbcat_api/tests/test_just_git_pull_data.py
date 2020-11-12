import logging

from ifbcat_api.tests.test_with_importdata import EnsureImportDataAreHere

logger = logging.getLogger(__name__)


class LoadBioinfoTeamsTestCase(EnsureImportDataAreHere):
    def test_ok(self):
        pass
