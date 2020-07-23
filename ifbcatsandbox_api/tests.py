from django.test import TestCase
from factory.random import reseed_random

from ifbcatsandbox_api import factories

# to have test reproducible
reseed_random(0)


class ExampleTestCase(TestCase):
    def test_nothing(self):
        u = factories.UserFactory()
        print(u, u.groups.all())
        print(factories.EventKeywordFactory())
        print(factories.EventPrerequisiteFactory())
        print(factories.EventTopicFactory())
        pf = factories.ElixirPlatformFactory(coordinator=u, deputies=[u] + [factories.UserFactory() for _ in range(2)])
        print(pf.name, pf.coordinator, pf.deputies.all())
