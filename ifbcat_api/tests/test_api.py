import re
from collections import defaultdict

from django.urls import reverse

from ifbcat_api.tests.test_no_views_crash import TestCaseWithData


class TestApi(TestCaseWithData):
    by_passed_links = {
        'http://testserver/api/team/Pasteur%20HUB/',
    }

    def test_create_new_file(self):
        response = self.client.get(reverse('sitemap-general'))
        resp = response.content.decode()
        url_pattern = r'<loc>(.*?)</loc>'
        links = re.findall(url_pattern, resp)
        grouped_links = defaultdict(set)

        for link in links:
            group = link.find('/', link.find('api') + 4)
            grouped_links[group].add(link)

        for links in grouped_links.values():
            links_to_test = list(links)[:10]
            links_to_test.extend(self.by_passed_links & links)

            for link in links_to_test:
                self.assertEqual(self.client.get(link, follow=True).status_code, 200, link)
