from rest_framework import serializers

from ifbcat_api import models, misc


class OrganisationInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Organisation
        fields = [
            'id',
            'name',
            'url',
        ]

    url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='organisation-detail',
        lookup_field='name',
    )


class CommunityInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Community
        fields = [
            'id',
            'name',
            'url',
        ]

    url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='community-detail',
        lookup_field='name',
    )


class ElixirPlatformInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ElixirPlatform
        fields = [
            'id',
            'name',
            'url',
        ]

    url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='elixirplatform-detail',
        lookup_field='name',
    )


EventInlineSerializer = misc.inline_serializer_factory(models.Event)
TeamInlineSerializer = misc.inline_serializer_factory(models.Team, lookup_field='name')
TrainingInlineSerializer = misc.inline_serializer_factory(models.Training)
TrainingMaterialInlineSerializer = misc.inline_serializer_factory(models.TrainingMaterial, url=False)


class EventSponsorInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.EventSponsor
        fields = [
            'id',
            'name',
            'url',
        ]

    url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='eventsponsor-detail',
        lookup_field='name',
    )
