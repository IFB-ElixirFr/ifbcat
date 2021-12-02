import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.test import TestCase

logger = logging.getLogger(__name__)


class TestOpenapiWorks(TestCase):
    def test_it(self):
        u = get_user_model()(email="a@aa.com", firstname="a", lastname="a", password=make_password("test"))
        u.full_clean()
        u = get_user_model()(email="a@Aa.com", firstname="a", lastname="a", password=make_password("test"))
        self.assertRaises(ValidationError, u.full_clean)
