# Imports
from django.contrib.auth import get_user_model
from django.db.models import ManyToManyField, ManyToOneRel, ManyToManyRel
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

        # Check whether object being updated matches the authenticated user profile.
        # When a request is authenticated, the authenticated user profile is assigned
        # to the request, so we can ensure this has the same id as the object.
        # i.e. will return True if they're trying to update their own profile.
        return obj.id == request.user.id


# Custom permissions class for updating object
class ReadWriteBySomething(permissions.BasePermission):
    class Meta:
        abstract = True

    """Allow everyone to see, but only target to update/delete."""
    target = None
    """Allow everyone to see, but only update/delete if one targets match."""
    targets = None

    def __init__(self, *args, **kwargs):
        assert self.target is not None or self.targets is not None, "target cannot be None"
        assert (self.target is None and self.targets is not None) or (
            self.target is not None and self.targets is None
        ), "either define target or targets, not both"
        if self.target:
            self.targets = [self.target]

    def has_object_permission(self, request, view, obj):
        for target in self.targets:
            # check if __ is in the target, if so we use the queryset to filter and check if the object is
            # still accessible
            # we get the target attribute
            target_attr = getattr(obj, target, None)
            if '__' in target:
                if obj._meta.model.objects.filter(**{target: request.user, "id": obj.id}).exists():
                    return True
            # if it is a ManyToMany we test if the user on of them
            elif isinstance(obj._meta.get_field(target), ManyToManyField):
                if target_attr.filter(id=request.user.id).exists():
                    return True
            # otherwise we test is the user is the target
            elif target_attr is not None and target_attr.id == request.user.id:
                return True
        return False


# Custom permissions class for updating object
class ReadOnly(permissions.BasePermission):
    """Allow everyone to see, but no one to update/delete."""

    def has_permission(self, request, view):
        """Check the user is trying to update their own object."""
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        """Check the user is trying to update their own object."""
        return request.method in permissions.SAFE_METHODS


class ReadWriteByUser(ReadWriteBySomething):
    target = 'user'


class ReadWriteByCoordinator(ReadWriteBySomething):
    target = 'coordinator'


class ReadWriteByTrainers(ReadWriteBySomething):
    target = 'trainers'


class ReadWriteByLeader(ReadWriteBySomething):
    targets = [
        'leaders',
        'scientificLeaders',
        'technicalLeaders',
    ]


class ReadWriteByDeputies(ReadWriteBySomething):
    target = 'deputies'


class ReadWriteByMaintainers(ReadWriteBySomething):
    target = 'maintainers'


class ReadWriteByAuthors(ReadWriteBySomething):
    target = 'authors'


class ReadWriteBySubmitters(ReadWriteBySomething):
    target = 'submitters'


class ReadWriteByTeamLeaders(ReadWriteBySomething):
    targets = [
        'team__leaders',
        'team__scientificLeaders',
        'team__technicalLeaders',
    ]


class ReadWriteByTeamDeputies(ReadWriteBySomething):
    target = 'team__deputies'


class ReadWriteByTeamMaintainers(ReadWriteBySomething):
    target = 'team__maintainers'


class ReadWriteByTeamsLeader(ReadWriteBySomething):
    targets = [
        'teams__leaders',
        'teams__scientificLeaders',
        'teams__technicalLeaders',
    ]


class ReadWriteByTeamsDeputies(ReadWriteBySomething):
    target = 'teams__deputies'


class ReadWriteByTeamsMaintainers(ReadWriteBySomething):
    target = 'teams__maintainers'


class ReadWriteByOrgByTeamsLeader(ReadWriteBySomething):
    targets = [
        'organisedByTeams__leaders',
        'organisedByTeams__scientificLeaders',
        'organisedByTeams__technicalLeaders',
    ]


class ReadWriteByOrgByTeamsDeputies(ReadWriteBySomething):
    target = 'organisedByTeams__deputies'


class ReadWriteByOrgByTeamsMaintainers(ReadWriteBySomething):
    target = 'organisedByTeams__maintainers'


# class ReadWriteByOrgByOrganisationsLeader(ReadWriteBySomething):
#     target = 'organisedByOrganisations__user_profile'


class ReadWriteByProvidedByLeader(ReadWriteBySomething):
    targets = [
        'providedBy__leaders',
        'providedBy__scientificLeaders',
        'providedBy__technicalLeaders',
    ]


class ReadWriteByProvidedByDeputies(ReadWriteBySomething):
    target = 'providedBy__deputies'


class ReadWriteByProvidedByMaintainer(ReadWriteBySomething):
    target = 'providedBy__maintainers'


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


class ReadWriteBySuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser


class ReadWriteBySuperEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        from ifbcat_api import business_logic

        return business_logic.is_super_editor(request.user)

    def has_object_permission(self, request, view, obj):
        from ifbcat_api import business_logic

        return business_logic.is_super_editor(request.user)


class ReadWriteByCurator(permissions.BasePermission):
    def has_permission(self, request, view):
        from ifbcat_api import business_logic

        return business_logic.is_curator(request.user)

    def has_object_permission(self, request, view, obj):
        from ifbcat_api import business_logic

        return business_logic.is_curator(request.user)


class ReadWriteByUserManager(permissions.BasePermission):
    def has_permission(self, request, view):
        from ifbcat_api import business_logic

        return business_logic.is_user_manager(request.user)

    def has_object_permission(self, request, view, obj):
        from ifbcat_api import business_logic

        return business_logic.is_user_manager(request.user) or (
            isinstance(obj, get_user_model()) and business_logic.can_edit_user(request.user, obj)
        )


class UserCanAddNew(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in ("PUT", "POST")

    def has_object_permission(self, request, view, obj):
        return obj is None


class UserCanEditAndDeleteIfNotUsed(permissions.BasePermission):
    allowed_methods = ("PUT", "POST", "DELETE")

    def has_permission(self, request, view):
        return request.method in self.allowed_methods

    def has_object_permission(self, request, view, obj):
        if request.method not in self.allowed_methods:
            return False
        for model_field in obj._meta.get_fields():
            if isinstance(model_field, ManyToManyRel) or isinstance(model_field, ManyToOneRel):
                attr_name = model_field.related_name or (model_field.name + "_set")
                if getattr(obj, attr_name).count() > 0:
                    return False
        return True


class UserCanDeleteIfNotUsed(UserCanEditAndDeleteIfNotUsed):
    allowed_methods = ("DELETE",)


class UserCanEditIfNotStaff(permissions.BasePermission):
    allowed_methods = ("PUT", "POST")

    def has_permission(self, request, view):
        return request.method in self.allowed_methods

    def has_object_permission(self, request, view, obj):
        if request.method not in self.allowed_methods:
            return False
        if obj is not None and (obj.is_staff or obj.is_superuser):
            return False
        return True


class UserCanDeleteIfNotStaffAndNotUsed(permissions.BasePermission):
    allowed_methods = ("DELETE",)

    def has_permission(self, request, view):
        return request.method in self.allowed_methods

    def has_object_permission(self, request, view, obj):
        if request.method not in self.allowed_methods:
            return False
        if obj is not None and (obj.is_staff or obj.is_superuser):
            return False
        for model_field in obj._meta.get_fields():
            if isinstance(model_field, ManyToManyRel) or isinstance(model_field, ManyToOneRel):
                attr_name = model_field.related_name or (model_field.name + "_set")
                if hasattr(obj, attr_name) and getattr(obj, attr_name).count() > 0:
                    return False
        return True


class IsFromAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        from ifbcat_api import business_logic

        return business_logic.is_from_admin(request)

    def has_object_permission(self, request, view, obj):
        from ifbcat_api import business_logic

        return business_logic.is_from_admin(request)


class SuperuserCanDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser and request.method == "DELETE"

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser and request.method == "DELETE"
