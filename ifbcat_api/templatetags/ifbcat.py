import itertools
import logging
from typing import List, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.template import Library, Context
from jazzmin.templatetags.jazzmin import get_side_menu

from ifbcat_api import models

User = get_user_model()
register = Library()
logger = logging.getLogger(__name__)


@register.simple_tag(takes_context=True)
def get_editable_instance(context: Context) -> List[Dict]:
    user = context.get("user")
    if not user:
        return []
    editable = []
    for model in itertools.chain(*[a["models"] for a in get_side_menu(context, using="app_list")]):
        model['my'] = True
        if model['object_name'] == 'Team':
            if model['perms']['change']:
                model['instances'] = models.Team.objects.filter(Q(leader=user) | Q(maintainers=user) | Q(deputies=user))
                editable.append(model)
        # elif model['object_name'] == 'Organisation':
        #     if model['perms']['change']:
        #         model['instances'] = models.Organisation.objects.filter(Q(user_profile=user))
        #         editable.append(model)
        elif model['object_name'] == 'Group':
            if model['perms']['change']:
                model['instances'] = Group.objects.all()
                model['my'] = False
                editable.append(model)
        elif model['object_name'] == 'Training':
            if model['perms']['change']:
                model['action_url'] = 'new_training_course'
                model['action_text'] = "Add a new session"
                model['instances'] = models.Training.objects.filter(
                    Q(contactId=user)
                    | Q(elixirPlatforms__coordinator=user)
                    | Q(elixirPlatforms__deputies=user)
                    | Q(organisedByTeams__leader=user)
                    | Q(organisedByTeams__deputies=user)
                    | Q(organisedByTeams__maintainers=user)
                )
                editable.append(model)
        elif model['object_name'] == 'Event':
            if model['perms']['change']:
                model['instances'] = models.Event.objects.filter(
                    Q(contactId=user)
                    | Q(trainers__trainerId=user)
                    | Q(elixirPlatforms__coordinator=user)
                    | Q(elixirPlatforms__deputies=user)
                    | Q(organisedByTeams__leader=user)
                    | Q(organisedByTeams__deputies=user)
                    | Q(organisedByTeams__maintainers=user)
                )
                editable.append(model)
    return editable
