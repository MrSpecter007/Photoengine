from home.models import HomePage

from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase


class HomeSetUpTests(WagtailPageTestCase):
    """
    Tests for basic page structure setup and HomePage creation.
    """

    def test_root_create(self):
        root_page = Page.objects.get(pk=1)
        self.assertIsNotNone(root_page)

    def test_homepage_create(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage(title="Home Secondary", slug="home-secondary")
        root_page.add_child(instance=homepage)
        self.assertTrue(HomePage.objects.filter(title="Home Secondary").exists())


class HomeTests(WagtailPageTestCase):
    """
    Tests for homepage functionality and rendering.
    """

    def setUp(self):
        """
        Use the Wagtail-served homepage created by migrations.
        """
        self.homepage = HomePage.objects.first()
        if self.homepage is None:
            root_page = Page.objects.get(pk=1)
            self.homepage = HomePage(title="Home", slug="home")
            root_page.add_child(instance=self.homepage)

    def test_homepage_status_code(self):
        response = self.client.get(self.homepage.url)
        self.assertEqual(response.status_code, 200)

    def test_homepage_template_used(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")
