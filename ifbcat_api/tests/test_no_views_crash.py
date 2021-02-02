import logging

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.core.exceptions import FieldError
from django.urls import reverse, NoReverseMatch

from ifbcat_api.model.misc import Topic, Keyword, Field
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


class TestNoViewsCrash(EnsureImportDataAreHere):
    def setUp(self):
        super().setUp()
        # which view do not return 200 and it is normal
        self.status_code_not_200 = {
            "trainingevent-list": 403,
            "trainingevent-detail": 403,
        }

        # load the whole catalogue
        management.call_command('load_catalog')

        # create some instance to add everywhere, allows to test all HyperlinkedModelSerializer and *SlugRelatedField
        k, _ = Keyword.objects.get_or_create(keyword="café")
        add_everywhere(k)
        t, _ = Topic.objects.get_or_create(uri="http://edamontology.org/topic_0091")
        add_everywhere(t)
        f, _ = Field.objects.get_or_create(field="django")
        add_everywhere(f)

    def test_all_at_once_to_spare_resource(self):
        #######################################################################
        # def test_list(self):
        #######################################################################
        cpt = 0
        for url_instance in [u for u in router.urls if u.name.endswith("-list")]:
            url_list = reverse(url_instance.name)
            response = self.client.get(url_list)
            status_code = self.status_code_not_200.get(url_instance.name, 200)
            self.assertEqual(
                response.status_code,
                status_code,
                f'failed while opening {url_instance.name} ({url_list}), expected {status_code} got {response.status_code}',
            )
            url_list += "?search=tralala"
            msg = f'failed while opening {url_instance.name} ({url_list}), expected {status_code} got {response.status_code}'
            try:
                response = self.client.get(url_list)
            except FieldError as e:
                self.assertTrue(False, msg + str(e))
            status_code = self.status_code_not_200.get(url_instance.name, 200)
            self.assertEqual(
                response.status_code,
                status_code,
                msg,
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
            status_code = self.status_code_not_200.get(url_instance.name, 200)
            for o in getattr(url_instance.callback.cls, "queryset").all():
                try:
                    url_detail = reverse(url_instance.name, kwargs={lookup_field: getattr(o, attr_field)})
                except (AttributeError, NoReverseMatch) as e:
                    raise Exception(
                        f'failed while opening {url_instance.name} with {o}',
                        e,
                    )
                response = self.client.get(url_detail)
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
