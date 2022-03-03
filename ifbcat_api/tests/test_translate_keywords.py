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
        models.Keyword.objects.create(keyword="KW1-fr")
        with NamedTemporaryFile(delete=True, suffix=".csv") as f:
            pass

        self.assertFalse(os.path.exists(f.name))
        management.call_command('translate_keywords', file=f.name)
        self.assertTrue(os.path.exists(f.name))

        with open(f.name, 'r') as data_file:
            self.assertEqual(
                len(data_file.readlines()),
                models.Keyword.objects.count() + 1,
                "1 plus the number of keyword to translate",
            )

        models.Keyword.objects.create(keyword="KW2-fr")
        management.call_command('translate_keywords', file=f.name)

        with open(f.name, 'r') as data_file:
            self.assertEqual(
                len(data_file.readlines()),
                models.Keyword.objects.count() + 1,
                "1 plus the number of keyword to translate",
            )
        models.Keyword.objects.create(keyword="KW3-fr")
        management.call_command('translate_keywords', file=f.name)

        with open(f.name, 'r') as data_file:
            self.assertEqual(
                len(data_file.readlines()),
                models.Keyword.objects.count() + 1,
                "1 plus the number of keyword to translate",
            )

    def test_append_to_empty_file(self):
        models.Keyword.objects.create(keyword="KW1")
        models.Keyword.objects.create(keyword="KW2")
        models.Keyword.objects.create(keyword="KW3")
        with NamedTemporaryFile(delete=True, suffix=".csv") as f:
            pass
        management.call_command('translate_keywords', file=f.name)

        with open(f.name, 'r') as data_file:
            data = csv.DictReader(data_file, delimiter=';')
            french_words = set(entry["French"] for entry in data)

        self.assertSetEqual(set(models.Keyword.objects.values_list("keyword", flat=True)), french_words, f.name)

    def test_translate_works_1(self):
        models.Keyword.objects.create(keyword="KW1-fr")  # will be translated
        models.Keyword.objects.create(keyword="KW2-en")  # is already translated
        models.Keyword.objects.create(keyword="KW3-fr")  # will be added
        models.Keyword.objects.create(keyword="KW4-fr")  # is not validated
        with NamedTemporaryFile(delete=False, suffix=".csv", mode="w") as f:
            f.write('French_keywords;English_keywords;Validated\n')
            f.write('KW1-fr;KW1-en;True\n')
            f.write('KW2-fr;KW2-en;True\n')
            f.write('KW4-fr;KW4-en;False\n')
        management.call_command('translate_keywords', file=f.name)

        self.assertSetEqual(
            set(models.Keyword.objects.values_list("keyword", flat=True)),
            {
                "KW1-en",
                "KW2-en",
                "KW3-fr",
                "KW4-fr",
            },
            f.name,
        )
