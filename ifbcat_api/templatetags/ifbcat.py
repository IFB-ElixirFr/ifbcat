import itertools
import logging
from typing import List, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.template import Library, Context
from django.utils import timezone
from django.utils.safestring import mark_safe
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
                model['instances'] = models.Team.objects.filter(
                    Q(leaders=user) | Q(maintainers=user) | Q(deputies=user)
                )
                model['order'] = 3
                editable.append(model)
        # elif model['object_name'] == 'Organisation':
        #     if model['perms']['change']:
        #         model['instances'] = models.Organisation.objects.filter(Q(user_profile=user))
        #         editable.append(model)
        elif model['object_name'] == 'Group':
            if model['perms']['change']:
                model['instances'] = Group.objects.all()
                model['my'] = False
                model['order'] = 4
                editable.append(model)
        elif model['object_name'] == 'Training':
            if model['perms']['change']:
                model['actions'] = [
                    dict(url='new_training_course', text=mark_safe('<i class="fa fa-plus"></i> session')),
                    dict(url='view_training_courses', text=mark_safe('<i class="fa fa-eye"></i> sessions')),
                ]
                model['instances'] = models.Training.objects.filter(
                    Q(maintainers=user)
                    | Q(elixirPlatforms__coordinator=user)
                    | Q(elixirPlatforms__deputies=user)
                    | Q(organisedByTeams__leaders=user)
                    | Q(organisedByTeams__deputies=user)
                    | Q(organisedByTeams__maintainers=user)
                )
                model['order'] = 2
                editable.append(model)
        elif model['object_name'] == 'Event':
            if model['perms']['change']:
                model['instances'] = models.Event.objects.filter(
                    Q(maintainers=user)
                    | Q(trainers__trainerId=user)
                    | Q(elixirPlatforms__coordinator=user)
                    | Q(elixirPlatforms__deputies=user)
                    | Q(organisedByTeams__leaders=user)
                    | Q(organisedByTeams__deputies=user)
                    | Q(organisedByTeams__maintainers=user)
                ).order_by('-start_date')
                model['order'] = 1
                editable.append(model)
    editable = sorted(editable, key=lambda x: x.get("order", 1))
    for model in editable:
        model['instances'] = model['instances'].distinct()
    return editable


@register.simple_tag(takes_context=True)
def get_general_instance(context: Context) -> List[Dict]:
    user = context.get("user")
    if not user:
        return []
    model_list = []
    for model in itertools.chain(*[a["models"] for a in get_side_menu(context, using="app_list")]):
        model['my'] = True
        if model['object_name'] == 'Event':
            if model['perms']['change']:
                qs = models.Event.objects
                qs = qs.filter(is_draft=False)
                qs = qs.filter(
                    Q(start_date__gte=timezone.now()) | Q(end_date__isnull=False) & Q(end_date__gte=timezone.now())
                )
                qs = qs.order_by('-start_date')
                model['instances'] = qs

                model['order'] = 1
                model['my'] = False
                model['suffix'] = "Upcoming"
                model_list.append(model)
    model_list = sorted(model_list, key=lambda x: x.get("order", 1))
    return model_list
