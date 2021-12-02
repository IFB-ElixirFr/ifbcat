import logging

from django.test import TestCase
from django.urls import reverse

logger = logging.getLogger(__name__)


class TestOpenapiWorks(TestCase):
    def test_it(self):
        self.client.get(reverse('openapi-schema') + "?format=openapi-json")
