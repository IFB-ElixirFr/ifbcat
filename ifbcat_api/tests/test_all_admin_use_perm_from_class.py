import logging

from django.apps import apps
from django.contrib import admin as contrib_admin
from django.test import TestCase

from ifbcat_api import admin

logger = logging.getLogger(__name__)


class AllAdminUsePermFromClassTestCase(TestCase):
    def test_all_admin_use_perm_from_class(self):
        model_admin_allowed_to_not_inherite_from_PermissionInClassModelAdmin = []
        for model in apps.get_app_config('ifbcat_api').get_models():
            if model in model_admin_allowed_to_not_inherite_from_PermissionInClassModelAdmin:
                pass
            model_admin = contrib_admin.site._registry[model]
            self.assertIsInstance(
                model_admin,
                admin.PermissionInClassModelAdmin,
                f'If you want to use for {model} the ModelAdmin {model_admin}, it must inherits from '
                f'PermissionInClassModelAdmin for security reason. Refer to documentation, '
                f'or observe how it is done for Organisation model',
            )
