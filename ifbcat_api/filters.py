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

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, ManyToManyField, ManyToOneRel
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend


class AutoSubsetFilterSet(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.get_auto_subset_fields() or []:
            try:
                model_field = self._meta.model._meta.get_field(field_name)
            except FieldDoesNotExist:
                # additional filter field cannot be found in class
                continue
            if isinstance(model_field, ManyToOneRel):
                self.filters[field_name].queryset = self.filters[field_name].queryset.filter(
                    ~Q(**{f'{model_field.remote_field.name}__isnull': True})
                )
            if isinstance(model_field, ManyToManyField):
                self.filters[field_name].queryset = self.filters[field_name].queryset.filter(
                    ~Q(**{f'{model_field.related_query_name()}__isnull': True})
                )
            if not self.filters[field_name].queryset.exists():
                del self.filters[field_name]

    def get_auto_subset_fields(self):
        return self._meta.fields


class DjangoFilterAutoSubsetBackend(DjangoFilterBackend):
    filterset_base = AutoSubsetFilterSet
    raise_exception = True
