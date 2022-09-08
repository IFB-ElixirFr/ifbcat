import base64

from django.test import TestCase
from django.urls import reverse


class TestIt(TestCase):
    def test_plain(self):
        for md, html in [
            ("[aa](https://aa.com/)", '<p><a href="https://aa.com/">aa</a></p>'),
            (
                """# e

 * a
 * b
""",
                "<h1>e</h1>\n<ul>\n<li>a</li>\n<li>b</li>\n</ul>",
            ),
        ]:
            response = self.client.post(reverse('md_to_html'), data=dict(md=md))
            self.assertEqual(response.content.decode("UTF-8"), html)

    def test_in_base64(self):
        for md, html in [
            ("[aa](https://aa.com/)", '<p><a href="https://aa.com/">aa</a></p>'),
            (
                """# ee

 * a
 * [aa](https://aa.com/)
""",
                "<h1>ee</h1>\n<ul>\n<li>a</li>\n<li><a href=\"https://aa.com/\">aa</a></li>\n</ul>",
            ),
        ]:
            md_base64 = base64.b64encode(md.encode("ascii")).decode("ascii")
            response = self.client.post(reverse('md_to_html'), data=dict(md=md_base64, encoding="base64"))
            self.assertEqual(response.content.decode("UTF-8"), html)
