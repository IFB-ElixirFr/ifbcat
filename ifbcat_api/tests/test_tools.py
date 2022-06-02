from django.test import TestCase
from django.urls import reverse

from ifbcat_api import models


class TestIt(TestCase):
    def test_create_new_file(self):
        models.Tool.objects.create(biotoolsID="NotAnID")
        models.Tool.objects.create(biotoolsID="AgroLD")
