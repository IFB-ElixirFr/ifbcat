import csv
import logging
import os.path
from tempfile import NamedTemporaryFile

from django.core import management
from django.test import TestCase

from ifbcat_api import models

logger = logging.getLogger(__name__)


class TestLoadKeywords(TestCase):
    def test_create_new_file(self):
        with NamedTemporaryFile(delete=True, suffix=".csv") as f:
            pass

        self.assertFalse(os.path.exists(f.name))
        management.call_command('load_keywords_translate_from_csv', file=f.name)
        self.assertTrue(os.path.exists(f.name))

    def test_append_to_empty_file(self):
        models.Keyword.objects.create(keyword="KW1")
        models.Keyword.objects.create(keyword="KW2")
        models.Keyword.objects.create(keyword="KW3")
        with NamedTemporaryFile(delete=True, suffix=".csv") as f:
            pass
        management.call_command('load_keywords_translate_from_csv', file=f.name)

        with open(f.name, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter='\t')
            french_words = set(entry["French_keywords"] for entry in data)

        self.assertSetEqual(set(models.Keyword.objects.values_list("keyword", flat=True)), french_words, f.name)
