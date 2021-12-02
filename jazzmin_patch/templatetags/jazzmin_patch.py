from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


# credits: https://stackoverflow.com/a/18951166/2144569
@register.filter
@stringfilter
def template_exists(value):
    try:
        template.loader.get_template(value)
        return True
    except template.TemplateDoesNotExist:
        return False


@register.simple_tag
def patch_for_get_jazzmin_settings(request):
    request.current_app = getattr(request, 'current_app', None)
