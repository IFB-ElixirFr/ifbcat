# Imports
#
# "Response" is used to return responses from APIView
# "status" object holds HTTP status codes - used when returning responses from the API
# TokenAuthentication is used to users to authenticate themselves with the API
# "filters" is for filtering the ViewSets
# "ObtainAuthToken" is a view used to generate an auth token
# "api_settings" is used when configuring the custom ObtainAuthToken view
# "IsAuthenticatedOrReadOnly" is used to ensure that a ViewSet is read-only if the user is not autheticated.
# "IsAuthenticated" is used to block access to an entire ViewSet endpoint unless a user is autheticated

import warnings

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, ManyToManyField, ManyToOneRel
from django.urls import reverse, NoReverseMatch
from django_filters import rest_framework as django_filters
from django_filters.fields import ModelMultipleChoiceField
from django_filters.rest_framework import DjangoFilterBackend


class AutoSubsetFilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.get_auto_subset_fields() or []:
            check_qs = False
            try:
                model_field = self._meta.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                # additional filter field cannot be found in class
                continue
            if isinstance(model_field, ManyToOneRel):
                self.filters[field_name].queryset = self.filters[field_name].queryset.filter(
                    ~Q(**{f'{model_field.remote_field.name}__isnull': True})
                )
                check_qs = True
            if isinstance(model_field, ManyToManyField):
                self.filters[field_name].queryset = self.filters[field_name].queryset.filter(
                    ~Q(**{f'{model_field.related_query_name()}__isnull': True})
                )
                check_qs = True
            if check_qs and not self.filters[field_name].queryset.exists():
                self.filters[field_name].field.widget.attrs["disabled"] = True

    def get_auto_subset_fields(self):
        return self._meta.fields


class DjangoFilterAutoSubsetBackend(DjangoFilterBackend):
    filterset_base = AutoSubsetFilterSet
    raise_exception = True

    def get_schema_operation_parameters(self, view):
        try:
            queryset = view.get_queryset()
        except Exception:
            queryset = None
            warnings.warn("{} is not compatible with schema generation".format(view.__class__))

        filterset_class = self.get_filterset_class(view, queryset)

        if not filterset_class:
            return []

        parameters = []
        for field_name, field in filterset_class.base_filters.items():
            parameter = {
                'name': field_name,
                'required': field.extra['required'],
                'in': 'query',
                'description': field.label if field.label is not None else field_name,
                'schema': {
                    'type': 'string',
                },
            }
            if field.extra and 'choices' in field.extra:
                parameter['schema']['enum'] = [c[0] for c in field.extra['choices']]
            if field.field_class == ModelMultipleChoiceField:
                try:
                    parameter['schema']['endpoint'] = reverse(get_list_view_name(field.queryset.model))
                    parameter['schema']['type'] = 'id'
                    need_choices = False
                except NoReverseMatch:
                    need_choices = True
                choices_count_in_schema = settings.MAX_CHOICES_COUNT_IN_SCHEMA
                if need_choices or choices_count_in_schema == -1 or field.queryset.count() < choices_count_in_schema:
                    parameter['schema']['type'] = 'id'
                    parameter['schema']['choices'] = [(o.id, str(o)) for o in field.queryset.all()]
            parameters.append(parameter)
        return parameters


def get_list_view_name(model):
    """
    Given a model class, return the view name to use for URL relationships
    that refer to instances of the model.
    inspiration : from rest_framework.utils.field_mapping.get_detail_view_name
    """
    return '%(model_name)s-list' % {'app_label': model._meta.app_label, 'model_name': model._meta.object_name.lower()}
