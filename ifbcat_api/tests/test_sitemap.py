import re
from collections import defaultdict

from django.urls import reverse

from ifbcat_api import models
from ifbcat_api.tests.test_no_views_crash import TestCaseWithData


class TestApi(TestCaseWithData):
    by_passed_links = {
        'http://testserver/api/team/Pasteur%20HUB/',
    }
    link_count_to_test = 10

    def test_create_new_file(self):
        response = self.client.get(reverse('sitemap-general'))
        resp = response.content.decode()
        url_pattern = r'<loc>(.*?)</loc>'
        links = re.findall(url_pattern, resp)
        grouped_links = defaultdict(set)

        for link in links:
            group = link.find('/', link.find('api') + 4)
            grouped_links[group].add(link)

        total = 0
        for links in grouped_links.values():
            links_to_test = list(links)[: self.link_count_to_test]
            links_to_test.extend(self.by_passed_links & links)

            for link in links_to_test:
                self.assertEqual(self.client.get(link, follow=True).status_code, 200, link)
                total += 1
        self.assertGreater(total, 0)


class TestApiCustomInstance(TestApi):
    link_count_to_test = 1000

    def setUp(self):
        # don't call super().setUp(), create instance instead, can only be an instance in the sitemap
        models.Team.objects.get_or_create(
            name="foo",
        )
