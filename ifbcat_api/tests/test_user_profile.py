import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

logger = logging.getLogger(__name__)


class TestOpenapiWorks(TestCase):
    def test_it(self):
        get_user_model().objects.create(email="a.a@a", firstname="a", lastname="a")
        self.assertRaises(ValidationError, get_user_model().objects.create, email="a.A@a", firstname="a", lastname="a")
