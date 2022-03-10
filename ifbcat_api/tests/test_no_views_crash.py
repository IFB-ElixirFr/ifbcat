import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.core.exceptions import FieldError
from django.test import TestCase
from django.urls import reverse, NoReverseMatch

from ifbcat_api.model.misc import Topic, Keyword, Field
from ifbcat_api.model.userProfile import UserProfile
from ifbcat_api.model.organisation import Organisation
from ifbcat_api.model.team import Team
from ifbcat_api.tests.test_with_importdata import EnsureImportDataAreHere
from ifbcat_api.urls import router

logger = logging.getLogger(__name__)


def add_everywhere(instance):
    """
    A magical function that take an instance, find in its attributes which are M2M, and add the current instance to the
    first instance of this class. For example with a Topic instance t, this function will be equivalent to
    userProfile.objects.first().expertise.add(t)
    :param instance:
    :return:
    """
    for a in [
        a
        for a in dir(instance)
        if a[0] != '_'
        and a
        not in [
            "objects",
            "DoesNotExists",
        ]
    ]:
        if not hasattr(getattr(instance, a), "model"):
            continue
        manager = getattr(instance, a).model.objects
        if not manager.exists():
            continue
        related_instance = manager.first()
        for f in related_instance._meta.get_fields():
            if f.related_model == instance.__class__:
                getattr(related_instance, f.name).add(instance)


class TestNoViewsCrashWithoutData(TestCase):
    def setUp(self):
        self.superuser, _ = get_user_model().objects.get_or_create(
            is_superuser=True,
            is_staff=True,
            defaults=dict(
                firstname="superuser",
                lastname="ifb",
                email='superuser@ifb.fr',
            ),
        )

    def test_dashboard(self):
        self.client.force_login(self.superuser)
        self.assertEqual(self.client.get('/admin/').status_code, 200)


class TestNoViewsCrash(EnsureImportDataAreHere):
    def setUp(self):
        super().setUp()
        # load the whole catalogue
        management.call_command('load_catalog')

        # create some instance to add everywhere, allows to test all HyperlinkedModelSerializer and *SlugRelatedField
        k, _ = Keyword.objects.get_or_create(keyword="café")
        add_everywhere(k)
        t, _ = Topic.objects.get_or_create(uri="http://edamontology.org/topic_0091")
        add_everywhere(t)
        f, _ = Field.objects.get_or_create(field="django")
        add_everywhere(f)
        logger.warning('Data loaded')

    def test_all_at_once_to_spare_resource(self):
        #######################################################################
        # test_loadcatalog
        #######################################################################
        self.assertEqual(
            UserProfile.objects.count(),
            715,
        )
        self.assertEqual(
            Team.objects.count(),
            36,
        )
        self.assertEqual(
            Organisation.objects.count(),
            76,
        )
        available_formats_dict = dict()
        ignored_formats = {'rdf'}
        #######################################################################
        # def test_list(self):
        #######################################################################
        cpt = 0
        for prefix, viewset, basename in router.registry:
            url_list = reverse(f'{basename}-list')
            available_formats = set(r.format for r in viewset.renderer_classes) - ignored_formats
            available_formats_dict[basename] = available_formats
            for suffix in [
                "",
                "?search=tralala",
            ] + [f'?format={fmt}' for fmt in available_formats]:
                response = self.client.get(url_list + suffix)
                status_code = 200
                self.assertEqual(
                    response.status_code,
                    status_code,
                    f'failed while opening {basename}-list '
                    f'({url_list}{suffix}), expected {status_code} '
                    f'got {response.status_code}',
                )
            cpt += 1
        self.assertGreater(cpt, 0)

        #######################################################################
        # def test_detail(self):
        #######################################################################
        cpt = 0
        for url_instance in [u for u in router.urls if u.name.endswith("-detail")]:
            lookup_field = getattr(url_instance.callback.cls, "lookup_field")
            attr_field = lookup_field.replace("__unaccent", "")
            attr_field = attr_field.replace("__iexact", "")
            available_formats = available_formats_dict[url_instance.name[:-7]]
            for o in getattr(url_instance.callback.cls, "queryset").all():
                try:
                    url_detail = reverse(url_instance.name, kwargs={lookup_field: getattr(o, attr_field)})
                except (AttributeError, NoReverseMatch) as e:
                    raise Exception(
                        f'failed while opening {url_instance.name} with {o}',
                        e,
                    )
                for suffix in [
                    "",
                ] + [f'?format={fmt}' for fmt in available_formats]:
                    response = self.client.get(url_detail + suffix)
                    status_code = 200
                    self.assertEqual(
                        response.status_code,
                        status_code,
                        f'failed while opening {url_instance.name} ({url_detail}), expected {status_code} got {response.status_code}',
                    )
                    cpt += 1
        self.assertGreater(cpt, 0)

        #######################################################################
        # def test_admin_list(self):
        #######################################################################
        self.client.force_login(self.superuser)
        for ifbcat_api_model in apps.get_app_config('ifbcat_api').get_models():
            content_type = ContentType.objects.get_for_model(ifbcat_api_model)

            url_list = reverse("admin:%s_%s_changelist" % (content_type.app_label, content_type.model))
            response = self.client.get(url_list)
            status_code = 200
            self.assertEqual(
                response.status_code,
                status_code,
                f'failed while opening admin list view for {ifbcat_api_model} ({url_list}), '
                f'expected {status_code} got {response.status_code}',
            )
            url_list += "?q=tralala"
            msg = (
                f'failed while opening admin list view for {ifbcat_api_model} ({url_list}), '
                f'expected {status_code} got {response.status_code}'
            )
            try:
                response = self.client.get(url_list)
            except FieldError:
                self.assertTrue(False, msg)
            status_code = 200
            self.assertEqual(
                response.status_code,
                status_code,
                msg,
            )

        #######################################################################
        # def test_admin_detail(self):
        #######################################################################
        for ifbcat_api_model in apps.get_app_config('ifbcat_api').get_models():
            content_type = ContentType.objects.get_for_model(ifbcat_api_model)
            for o in ifbcat_api_model.objects.all()[:20]:
                url_detail = reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(o.id,))
                response = self.client.get(url_detail)
                status_code = 200
                self.assertEqual(
                    response.status_code,
                    status_code,
                    f'failed while opening admin detail view for {ifbcat_api_model} (pk={o.id}) ({url_detail}), '
                    f'expected {status_code} got {response.status_code}',
                )
