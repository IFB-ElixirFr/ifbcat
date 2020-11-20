import logging
from unittest.util import safe_repr

from django.apps import apps
from django.contrib import admin as contrib_admin
from django.test import TestCase
from rest_framework import viewsets

from ifbcat_api import admin, views
from ifbcat_api import urls

logger = logging.getLogger(__name__)


class AllUsePermFromClassTestCase(TestCase):
    def setUp(self) -> None:
        self.model_admin_allowed_to_not_inherite_from_PermissionInClassModelAdmin = [
            None,
        ]
        self.viewset_allowed_to_not_inherite_from_PermissionInClassModelViewSet = [
            None,
        ]

    def assertIsSubClass(self, c, cls, msg=None):
        """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
        default message."""
        if not issubclass(c, cls):
            standardMsg = '%s is not a subclass of %r' % (safe_repr(c), cls)
            self.fail(self._formatMessage(msg, standardMsg))

    def test_all_admin_use_perm_from_class(self):
        for model in apps.get_app_config('ifbcat_api').get_models():
            if model in self.model_admin_allowed_to_not_inherite_from_PermissionInClassModelAdmin:
                continue
            model_admin = contrib_admin.site._registry[model]
            self.assertIsInstance(
                model_admin,
                admin.PermissionInClassModelAdmin,
                f'If you want to use for {model} the ModelAdmin {model_admin}, it must inherits from '
                f'PermissionInClassModelAdmin for security reason. Refer to documentation, '
                f'or observe how it is done for Organisation model',
            )

    def test_all_viewset_use_perm_from_class(self):
        for _, viewset, _ in urls.router.registry:
            if not issubclass(viewset, viewsets.ModelViewSet):
                continue
            if viewset in self.viewset_allowed_to_not_inherite_from_PermissionInClassModelViewSet:
                continue
            self.assertIsSubClass(
                viewset,
                views.PermissionInClassModelViewSet,
                f'If you want to use for {viewset.queryset.model} the ModelViewSet {viewset}, it must inherits from '
                f'views.PermissionInClassModelViewSet for security reason. Refer to documentation, '
                f'or observe how it is done for Organisation model',
            )
