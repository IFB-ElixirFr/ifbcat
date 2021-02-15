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
