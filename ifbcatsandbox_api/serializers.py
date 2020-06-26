from rest_framework import serializers

# This is just for testing serialization
class ChangelogSerializer(serializers.Serializer):
    """Serializes a test input field."""
    testinput = serializers.CharField(max_length=10)
