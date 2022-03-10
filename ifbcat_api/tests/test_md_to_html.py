from django.test import TestCase
from django.urls import reverse


class TestIt(TestCase):
    def test_create_new_file(self):
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
