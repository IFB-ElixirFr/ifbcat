# Imports
from rest_framework import permissions

# Custom permission class
class UpdateOwnProfile(permissions.BasePermission):
    """Allow users to edit their own profile (but not others)."""

    # This function gets called whenever request is made to the API that
    # the permission is assigned to - returns True or False depending on
    # whether the authenticated user has permission to do the change they're attempting.
    # obj is the object being edited.
    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own profile."""

        # Safe methods e.g. HTTP GET dont make any changes to the object - users
        # are allowed to view other user's profiles.
        if request.method in permissions.SAFE_METHODS:
            return True

         # Check whether object being updated matches the authenticated user profile.
         # When a request is authenticated, the authenticated user profile is assigned
         # to the request, so we can ensure this has the same id as the object.
         # i.e. will return True if they're trying to update their own profile.
        return obj.id == request.user.id
