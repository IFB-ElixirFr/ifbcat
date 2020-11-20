# Imports
from django.db.models import ManyToManyField
from rest_framework import permissions

# Custom permission class for updating user profiles
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


# Custom permissions class for updating object
class PubliclyReadableEditableBySomething(permissions.BasePermission):
    class Meta:
        abstract = True

    """Allow everyone to see, but only target to update/delete."""
    target = None

    def __init__(self, *args, **kwargs):
        assert self.target is not None, "target cannot be None"

    def has_object_permission(self, request, view, obj):
        """Check the user is trying to update their own object."""

        if request.method in permissions.SAFE_METHODS:
            return True

        # Check that the user owns the object, i.e. the user_profile associated
        # with the object is assigned to the user making the request.
        # (returns True if the object being updated etc. has a user profile id that matches the request)
        target_attr = getattr(obj, self.target)
        if isinstance(obj._meta.get_field(self.target), ManyToManyField):
            return target_attr.filter(id=request.user.id).exists()
        return target_attr is not None and target_attr.id == request.user.id


# Custom permissions class for updating object
class PubliclyReadableByUsers(permissions.BasePermission):
    """Allow everyone to see, but no one to update/delete."""

    def has_permission(self, request, view):
        """Check the user is trying to update their own object."""
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        """Check the user is trying to update their own object."""
        return request.method in permissions.SAFE_METHODS


class PubliclyReadableEditableByOwner(PubliclyReadableEditableBySomething):
    target = 'user_profile'


class PubliclyReadableEditableByCoordinator(PubliclyReadableEditableBySomething):
    target = 'coordinator'


class PubliclyReadableEditableByTrainers(PubliclyReadableEditableBySomething):
    target = 'trainers'


class PubliclyReadableEditableByMembers(PubliclyReadableEditableBySomething):
    target = 'members'


class PubliclyReadableEditableByContact(PubliclyReadableEditableBySomething):
    target = 'contactId'


class PubliclyReadableEditableByAuthors(PubliclyReadableEditableBySomething):
    target = 'authors'


class PubliclyReadableEditableBySubmitters(PubliclyReadableEditableBySomething):
    target = 'submitters'


class simple_override_method:
    def __init__(self, request, method):
        self.request = request
        self.method = method

    def __enter__(self):
        setattr(self.request, "former_method", self.request.method)
        self.request.method = self.method
        return self.request

    def __exit__(self, *args, **kwarg):
        self.request.method = self.request.former_method
        delattr(self.request, "former_method")


class PubliclyReadableByUsersEditableBySuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.method in permissions.SAFE_METHODS


class UserCanAddNew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS + ("PUT",)

    def has_object_permission(self, request, view, obj):
        return obj is None


class SuperuserCanDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser and request.method == "DELETE"

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser and request.method == "DELETE"
