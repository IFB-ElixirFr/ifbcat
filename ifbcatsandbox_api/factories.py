import factory
from django.contrib.auth.models import Group
from factory.fuzzy import FuzzyInteger

from . import models


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: "Group #%s" % n)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UserProfile

    firstname = factory.Faker('first_name')
    lastname = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda o: '%s.%s@example.org' % (o.firstname, o.lastname))
    groups = factory.SubFactory(GroupFactory)
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)


class EventKeywordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EventKeyword
        exclude = 'word'

    word = factory.Faker('word')
    keyword = factory.LazyAttribute(lambda p: 'kw_{}'.format(p.word))


class EventPrerequisiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EventPrerequisite
        exclude = 'word'

    word = factory.Faker('word')
    prerequisite = factory.LazyAttribute(lambda p: 'prq_{}'.format(p.word))


class EventTopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.EventTopic
        exclude = 'nb'

    nb = FuzzyInteger(0, 9999)
    topic = factory.LazyAttribute(lambda p: 'https://edamontology.org/topic_{}'.format(p.nb))


class ElixirPlatformFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ElixirPlatform

    name = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('sentence', nb_words=100)
    homepage = factory.Faker('url')
    coordinator = factory.SubFactory(UserFactory)

    @factory.post_generation
    def deputies(self, created, extracted, **kwargs):
        if extracted:
            for o in extracted:
                self.deputies.add(o)
