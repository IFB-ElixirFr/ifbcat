from django import template
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.log import get_admin_log
from django.contrib.contenttypes.models import ContentType

register = template.Library()


class AdminLogForInstanceNode(template.Node):
    def __init__(self, limit, varname, instance):
        self.limit, self.varname, self.instance_name = limit, varname, instance

    def __repr__(self):
        return "<GetAdminLog Node>"

    def render(self, context):
        instance = context[self.instance_name]
        entries = LogEntry.objects.filter(object_id=instance.id).filter(
            content_type=ContentType.objects.get_for_model(instance.__class__)
        )
        context[self.varname] = entries.select_related('content_type', 'user')[: int(self.limit)]
        return ''


@register.tag
def get_admin_log_for_instance(parser, token):
    """
    Populate a template variable with the admin log for the given criteria.

    Usage::

        {% get_admin_log [limit] as [varname] for_user [context_var_containing_user_obj] %}

    Examples::

        {% get_admin_log 10 as admin_log for_user 23 %}
        {% get_admin_log 10 as admin_log for_user user %}
        {% get_admin_log 10 as admin_log %}

    Note that ``context_var_containing_user_obj`` can be a hard-coded integer
    (user ID) or the name of a template context variable containing the user
    object whose ID you want.
    """
    tokens = token.contents.split()
    if len(tokens) < 6:
        return get_admin_log(parser, token)
    if len(tokens) < 4:
        raise template.TemplateSyntaxError("'get_admin_log' statements require two arguments")
    if not tokens[1].isdigit():
        raise template.TemplateSyntaxError("First argument to 'get_admin_log' must be an integer")
    if tokens[2] != 'as':
        raise template.TemplateSyntaxError("Second argument to 'get_admin_log' must be 'as'")
    if tokens[4] != 'for_instance':
        raise template.TemplateSyntaxError("fourth argument to 'get_admin_log' must be 'for_instance'")
    return AdminLogForInstanceNode(limit=tokens[1], varname=tokens[3], instance=tokens[5])
