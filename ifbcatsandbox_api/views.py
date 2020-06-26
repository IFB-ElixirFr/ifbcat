# Imports
# Response is used to return responses from APIView
from rest_framework.views import APIView
from rest_framework.response import Response

# StatusView is just a test API View, done in case APIView(s) are needed in the ifbcatsandbox API
class StatusView(APIView):
    """Test API View.  Currently just returns status of ifbcatsandbox API."""

    def get(self, request, format=None):
        """Returns the status of the ifbcatsandbox API."""
        status = [
        'ifbcatsandbox API  is available.',
        'Features:',
        '1. UserProfile model: customises default user model (to use email rather than username).',
        '   Support creation of normal and super-users.',
        '2. Djano Admin is configured and tested (available at /admin endpoint).',
        '3. /api/status endpoint: returns the implementation status of the API',
        ]

        return Response({'message': status})
