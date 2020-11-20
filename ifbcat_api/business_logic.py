import logging

from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from ifbcat_api import permissions
from ifbcat_api.model.userProfile import UserProfile

logger = logging.getLogger(__name__)

__USER_MANAGER_GRP_NAME = "User manager"


def __get_user_manager_group():
    g, created = Group.objects.get_or_create(name=__USER_MANAGER_GRP_NAME)
    if created or not g.permissions.exists():
        for action in ["view", "add", "change"]:
            g.permissions.add(
                Permission.objects.get(
                    codename=get_permission_codename(action, UserProfile._meta),
                    content_type=ContentType.objects.get_for_model(UserProfile),
                )
            )
    return g


def init_business_logic():
    __get_user_manager_group()


###############################################################################
# User manager
###############################################################################
def is_user_manager(user, request=None):
    return user.groups.filter(name=__USER_MANAGER_GRP_NAME).exists()


def get_user_manager_group_name():
    return __USER_MANAGER_GRP_NAME


def set_user_manager(user, status: bool):
    if status:
        user.groups.add(__get_user_manager_group())
    else:
        user.groups.remove(__get_user_manager_group())


def can_edit_user(acting_user, edited_user):
    return acting_user.groups.filter(name=__USER_MANAGER_GRP_NAME).exists()


###############################################################################
# Permission classes
###############################################################################
__missing_permission_classes = set()
__default_perm = permissions.PubliclyReadableByUsers


def get_permission_classes(model):
    if model == Group:
        return (permissions.PubliclyReadableByUsersEditableBySuperuser,)
    try:
        return model.get_permission_classes()
    except AttributeError:
        name = str(model.__name__)
        if name not in __missing_permission_classes:
            __missing_permission_classes.add(name)
            logger.info(f'No permission set in class for "{name}", ' f'using by default {__default_perm.__name__}')
        return (__default_perm,)
