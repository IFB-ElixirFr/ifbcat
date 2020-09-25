import logging
import os
from unittest.case import skipIf

from django.core import management
from django.test import TestCase

from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.team import Team

logger = logging.getLogger(__name__)

_test_data = "./test_data"
_import_data = "./import_data"


def has_git():
    return os.path.isfile("/usr/bin/git") or os.path.isfile("/usr/sbin/git")


def has_import_data():
    return os.path.isdir(_import_data)


@skipIf(not has_git() and not has_import_data(), "Cannot find git, neither the data in %s" % _import_data)
class EnsureImportDataAreHere(TestCase):
    class Meta:
        abstract = True

    test_data = _test_data
    import_data = _import_data

    def setUp(self):
        if has_git():
            if os.path.isdir(self.import_data):
                os.system('cd %s && git pull' % self.import_data)
            else:
                os.system('git clone git@github.com:IFB-ElixirFr/ifbcat-importdata.git %s' % self.import_data)
