import logging

from django.apps import apps
from django.contrib.auth import get_permission_codename, get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.authtoken.models import Token

from ifbcat_api import models
from ifbcat_api import permissions

logger = logging.getLogger(__name__)

__USER_MANAGER_GRP_NAME = "User manager"
__SUPER_EDITOR_GRP_NAME = "Supereditor (superuser that can also edit many things)"
__EVENT_GRP_NAME = "Event manager"
__TEAM_AND_MORE_GRP_NAME = "Community, Organisation, Project, Team manager"
__TOOL_GRP_NAME = "Tool manager"
__SERVICE_GRP_NAME = "Service manager"
__TRAINING_GRP_NAME = "Training manager"
__BASIC_PERMISSION_GRP_NAME = "Basic permissions for all admin"
__NO_RESTRICTION = "Grant access to all actions for all models of the catalog"


def __get_user_manager_group():
    g, created = Group.objects.get_or_create(name=__USER_MANAGER_GRP_NAME)
    if created or not g.permissions.exists():
        __init_user_manager_group(g)
    return g


def __init_user_manager_group(g):
    for action in ["view", "add", "change"]:
        g.permissions.add(
            Permission.objects.get(
                codename=get_permission_codename(action, models.UserProfile._meta),
                content_type=ContentType.objects.get_for_model(models.UserProfile),
            )
        )
    for action in ["view", "add"]:
        g.permissions.add(
            Permission.objects.get(
                codename=get_permission_codename(action, Group._meta),
                content_type=ContentType.objects.get_for_model(Group),
            )
        )
    return g


def __get_no_restriction_on_catalog_models_group():
    g, created = Group.objects.get_or_create(name=__NO_RESTRICTION)
    return g


def init_business_logic():
    for group_name in get_not_to_be_deleted_group_names():
        g, created = Group.objects.get_or_create(name=group_name)
        g.permissions.clear()
    user_manager_group = __get_user_manager_group()
    __init_user_manager_group(user_manager_group)
    no_restriction = __get_no_restriction_on_catalog_models_group()
    for app_label in [
        'ifbcat_api',
        'authtoken',
    ]:
        ifbcat_api_models = apps.get_app_config(app_label).get_models()
        for model in ifbcat_api_models:
            if model == get_user_model():
                continue
            for p in Permission.objects.filter(
                content_type=ContentType.objects.get_for_model(model),
            ):
                no_restriction.permissions.add(p)

    event_related = [
        models.EventCost,
        models.EventDate,
        models.EventPrerequisite,
        models.EventSponsor,
        models.Event,
    ]
    team_and_more_related = [
        models.Team,
        models.Certification,
        models.Team,
        models.Community,
        models.ElixirPlatform,
        models.Organisation,
        models.Project,
    ]
    tool_related = [
        models.Collection,
        models.ToolCredit,
        models.ToolType,
        models.Tool,
        models.OperatingSystem,
        models.TypeRole,
    ]
    service_related = [
        models.Service,
        models.ComputingFacility,
        models.ServiceSubmission,
    ]
    training_related = [
        models.AudienceRole,
        models.AudienceType,
        models.Trainer,
        models.TrainingEventMetrics,
        models.Training,
        models.TrainingMaterial,
    ]
    needed_by_all = [
        models.Doi,
        models.Field,
        models.Keyword,
        models.Topic,
        Token,
    ]

    _do_grants(__BASIC_PERMISSION_GRP_NAME, needed_by_all, ["view", "add", "change", "delete"])
    _do_grants(__BASIC_PERMISSION_GRP_NAME, [models.UserProfile], ["view", "change", "delete"])
    for some_models in [
        needed_by_all,
        training_related,
        service_related,
        tool_related,
        team_and_more_related,
        event_related,
    ]:
        _do_grants(__BASIC_PERMISSION_GRP_NAME, some_models, ["view"])
    _do_grants(__TRAINING_GRP_NAME, training_related, ["view", "add", "change", "delete"])
    _do_grants(__SERVICE_GRP_NAME, service_related, ["view", "add", "change", "delete"])
    _do_grants(__TOOL_GRP_NAME, tool_related, ["view", "add", "change", "delete"])
    _do_grants(__TEAM_AND_MORE_GRP_NAME, team_and_more_related, ["view", "add", "change", "delete"])
    _do_grants(__EVENT_GRP_NAME, event_related, ["view", "add", "change", "delete"])


def _do_grants(group_name, models_concerned, actions):
    g, created = Group.objects.get_or_create(name=group_name)
    for m in models_concerned:
        content_type = ContentType.objects.get_for_model(m)
        for action in actions:
            g.permissions.add(
                Permission.objects.get(
                    codename=get_permission_codename(action, m._meta),
                    content_type=content_type,
                )
            )


###############################################################################
# User manager
###############################################################################
def is_user_manager(user, request=None):
    user = user or request.user
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
# No restriction on catalog's models
###############################################################################
def has_no_restriction_on_catalog_models(user, request=None):
    return user.groups.filter(name=__NO_RESTRICTION).exists()


def get_no_restriction_on_catalog_models_name():
    return __NO_RESTRICTION


def set_no_restriction_on_catalog_models(user, status: bool):
    if status:
        user.groups.add(__get_user_manager_group())
    else:
        user.groups.remove(__get_user_manager_group())


###############################################################################
# Super editor
###############################################################################
def is_super_editor(user, request=None):
    user = user or request.user
    return user.is_superuser and user.groups.filter(name=__SUPER_EDITOR_GRP_NAME).exists()


###############################################################################
# Permission classes
###############################################################################
__missing_permission_classes = set()
__default_perm = permissions.ReadOnly


def get_permission_classes(model):
    if model == Group:
        return (permissions.ReadOnly | permissions.ReadWriteBySuperuser,)
    if model == Token:
        return (permissions.ReadWriteByUser | permissions.ReadWriteByUserManager | permissions.UserCanAddNew,)
    try:
        return model.get_permission_classes()
    except AttributeError:
        name = str(model.__name__)
        if name not in __missing_permission_classes:
            __missing_permission_classes.add(name)
            logger.info(f'No permission set in class for "{name}", ' f'using by default {__default_perm.__name__}')
        return (__default_perm,)


###############################################################################
# Permission classes
###############################################################################
def get_not_to_be_deleted_group_names():
    return (
        __USER_MANAGER_GRP_NAME,
        __SUPER_EDITOR_GRP_NAME,
        __EVENT_GRP_NAME,
        __TEAM_AND_MORE_GRP_NAME,
        __TOOL_GRP_NAME,
        __SERVICE_GRP_NAME,
        __TRAINING_GRP_NAME,
        __BASIC_PERMISSION_GRP_NAME,
        __NO_RESTRICTION,
    )
