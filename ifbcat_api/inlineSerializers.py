from rest_framework import serializers

from ifbcat_api import models


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


class TeamInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Team
        fields = [
            'id',
            'name',
            'url',
        ]

    url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='team-detail',
        lookup_field='name',
    )


class TrainingMaterialInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TrainingMaterial
        fields = [
            'id',
            'name',
            'url',
        ]

    url = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='team-detail',
        lookup_field='name',
    )


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
