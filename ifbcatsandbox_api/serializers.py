# Imports
# "re" is regular expression library
import re
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from ifbcatsandbox_api import models


# This is just for testing serialization
class TestApiViewSerializer(serializers.Serializer):
    """Serializes a test input field."""
    testinput = serializers.CharField(max_length=10)


# Model serializer for user profile
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes a user profile (UserProfile object)."""

    # Validation isn't specified for fields where basic validation defined in models.py is adequate
    # "allow_null" means None is considered a valid value (it defauls to False)
    # "required=False" means the field is not required to be present during (de)serialization (it defaults to True)
    # firstname, lastname and email are mandatory
    # NB. "allow_blank=False" means am empty string is considered invalid and will raise a validation error
    # (it is False by default, so no need to set it)

    # firstname (no further validation needed)
    # lastname (no further validation needed)
    # email (no further validation needed)
    orcidid = serializers.CharField(
        allow_blank=False,
        allow_null=True,
        required=False,
        validators=[UniqueValidator(queryset = models.UserProfile.objects.all())])
    homepage = serializers.URLField(allow_blank=False, allow_null=True, required=False)

    # Metaclass is used to configure the serializer to point to a specific object
    # and setup a list of fields in the model to manage with the serializer.
    class Meta:
        model = models.UserProfile
        fields = ('id', 'password', 'firstname', 'lastname', 'email', 'orcidid', 'homepage')

        # password field is set to be write-only - it should only be used when creating a new user profile
        # Would be security risk e.g. to allow password hash to be retrieved via API!
        # Also set the field style so that *** are given in the data entry field when the password is typed in
        extra_kwargs = {
            'password':
            {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

    # Validation logic
    def validate_orcidid(self, orcidid):
        """Validate supplied orcidid."""

        # orcidid is not mandatory - catch that
        if orcidid is None:
            return orcidid

        p = re.compile('^https?://orcid.org/[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$', re.IGNORECASE | re.UNICODE)
        if not p.search(orcidid):
            raise serializers.ValidationError('This field can only contain a valid ORCID ID.  Syntax: ^https?://orcid.org/[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$')
        return orcidid

    # Override the defult "create" function of the object manager, with the "create_user" function (defined in models.py)
    # This will ensure the password gets created as a hash, rather than clear text
    def create(self, validated_data):
        """Create and return a new user."""

        user = models.UserProfile.objects.create_user(
            password=validated_data['password'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            email=validated_data['email'],
            orcidid=validated_data['orcidid'],
            homepage=validated_data['homepage'])

        return user

    # Override the default "update" function to ensure the user password is hashed when updating
    # If this was not done, if a user updated their profile, the password field would be stored in cleartext,
    # and they'd be unable to login
    # NB.  we "pop" (assign the value and remove from the dictionary) the password from the validated data
    # and set is using "set_password" which saves the password as a hash
    # "super().update()" is used to pass the values to the Django REST update() method, to handle updating the remaining fields.
    def update(self, instance, validated_data):
        """Handle updating user account."""

        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)

        return super().update(instance, validated_data)


# News item serializer
class NewsItemSerializer(serializers.ModelSerializer):
    """Serializes a news item (NewsItem object)."""

    # news_text and created_on are mandatory

    # news_text (no further validation needed)
    # created_on (no further validation needed)

    class Meta:
        model = models.NewsItem
        # By default, Django adds a primary key ID ('id') to all models that are created.
        # It's read-only by default and gets an integer value that's incremented from the corresponding database table.
        # The other fields come from NewsItem.
        # NB. "created_on" is also auto-created (and thus read-only)
        # Don't want users to be able to set the user profile when creating a news item!
        # It must be set to the autheticated user.  Thus it's read-only.
        # Set read-only fields using the shortcut "read_only_fields" rather than extra_kwargs:
        #   extra_kwargs = {
        #      'user_profile': {'read_only': True}}

        fields = ('id', 'user_profile', 'news_text', 'created_on')
        read_only_fields = ['user_profile']


# Model serializer for event keyword
class EventKeywordSerializer(serializers.ModelSerializer):
    """Serializes an event keyword (EventKeyword object)."""

    keyword = serializers.CharField(allow_blank=False, required=False)

    class Meta:
        model = models.EventKeyword
        fields = ('id', 'keyword')
        extra_kwargs = {'id': {'read_only': True}}
        # fields = ('keyword')


# Model serializer for user profile
class EventSerializer(serializers.ModelSerializer):
    """Serializes an event (Event object)."""

    # CharField in ModelSerializer corresponds to both CharField and TextField in Django models
    # IntegerField in ModelSerializer corresponds to PositiveSmallIntegerField etc. in Django models
    # For BooleanField, if an input value is omitted in HTML-encoded form, it
    # is treated as setting the value to False. However, the default of "required=True"
    # is not set for them, and "allow_blank" is not supported.
    # See https://www.django-rest-framework.org/api-guide/fields/#booleanfield
    #
    # max_value of maxParticipants set to 32767 corresponding to PositiveSmallIntegerField defined in models.py
    # See https://www.geeksforgeeks.org/positivesmallintegerfield-django-models/
    #
    # "style={'base_template': 'textarea.html'}" sets the field style to an HTML textarea
    # See https://www.django-rest-framework.org/topics/html-and-forms/#field-styles
    #
    # "many=True" for keyword etc. instantiates a ListSerializer, see https://www.django-rest-framework.org/api-guide/serializers/#listserializer
    # "allow_empty=False" disallows empty lists as valid input.

    # name, description, homepage, accessibility, contactName and contactEmail are mandatory

    name = serializers.CharField()
    shortName = serializers.CharField(allow_blank=False, required=False)
    description = serializers.CharField(allow_blank=False, required=False, style={'base_template': 'textarea.html')
    homepage = serializers.URLField()

    type = serializers.ChoiceField(
        choices =  ('Workshop', 'Training course', 'Meeting', 'Conference'),
        allow_blank=True)

    # dates = ... TO_DO
    venue = serializers.CharField(allow_blank=False, required=False, style={'base_template': 'textarea.html'})
    city = serializers.CharField(allow_blank=False, required=False)
    country = serializers.CharField(allow_blank=False, required=False)
    onlineOnly = serializers.BooleanField(required=False)
    cost = serializers.ChoiceField(
        choices = ('Free', 'Free to academics', 'Concessions available'),
        allow_blank=True)
    # topic = ... TO_DO
    # keyword = EventKeywordSerializer(many=True, allow_empty=False, required=False)
    keywords = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field="keyword",
        queryset=models.EventKeyword.objects.all())
    # prerequisite = ... TO_DO
    accessibility = serializers.ChoiceField(
        choices = ('Public', 'Private'),
        allow_blank=True)
    accessibilityNote = serializers.CharField(allow_blank=False, required=False)
    maxParticipants = serializers.IntegerField(max_value=32767, min_value=1, required=False)
    contactName = serializers.CharField()
    contactEmail = serializers.EmailField()
    # contactId = ... TO_DO
    market = serializers.CharField(allow_blank=False, required=False)
    # elixirPlatform = ... TO_DO
    # community = ... TO_DO
    # hostedBy = ... TO_DO
    # organisedBy = ... TO_DO
    # sponsoredBy = ... TO_DO
    # logo = ... TO_DO


    # To-add to "fields" below:  dates', 'topic', 'prerequisite', 'contactId', 'elixirPlatform', 'community', 'hostedBy', 'organisedBy', 'sponsoredBy', 'logo'
    class Meta:
        model = models.Event

        fields = ('id', 'user_profile', 'name', 'shortName', 'description', 'homepage', 'type',
        'venue', 'city', 'country', 'onlineOnly', 'cost', 'keywords', 'accessibility', 'accessibilityNote',
        'maxParticipants', 'contactName', 'contactEmail', 'market')

        extra_kwargs = {
            'id': {'read_only': True},
            'user_profile': {'read_only': True}}
