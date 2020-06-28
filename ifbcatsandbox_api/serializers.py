# Imports
from rest_framework import serializers
from ifbcatsandbox_api import models

# This is just for testing serialization
class ChangelogSerializer(serializers.Serializer):
    """Serializes a test input field."""
    testinput = serializers.CharField(max_length=10)


# Model serializer
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes a user profile (UserProfile object)."""

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

    class Meta:
        model = models.NewsItem
        # By default, Django adds a primary key ID ('id') to all models that are created.
        # It's read-only and gets an integer value that's incremented from the corresponding database table.
        # The other fields come from NewsItem.
        # NB. "created_on" is also auto-created (and thus read-only)
        fields = ('id', 'user_profile', 'news_text', 'created_on')

        # Don't want users to be able to set the user profile when creating a news item!
        # It must be set to the autheticated user.  Thus it's read-only.
        extra_kwargs = {'user_profile': {'read_only': True}}
