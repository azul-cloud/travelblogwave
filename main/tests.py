from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from .models import Contact


class MainTestSetup(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'main_test_user', 
            'testuser@domain.com',
            'testpassword'
        )
        self.contact = Contact.objects.create(
            message='i''m sending you this message',
            type='G',
            user=self.user
        )

class MainViewTest(MainTestSetup):
    def test_home(self):
        url = reverse('main-home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CREATE BLOG")

    def test_about(self):
        url = reverse('main-about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_robots(self):
        url = reverse('robots')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_sitemap(self):
        url = reverse('sitemap')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class MainFormtest(MainTestSetup):
    def test_contact_form(self):
        url = reverse('main-contact')
        post = {
            "message":"hello this is a test",
            "type":"G"
        }
        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)

