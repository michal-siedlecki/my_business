from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from django.urls import reverse


class InvoiceViewsTests(TestCase):
    def test_about_view(self):
        """
        Test if we can see about app view
        :return: status code 200
        """

        client = Client()
        response = client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        """
        Test if we can see invoice list view
        :return: status code 200
        """
        self.user = User.objects.create_superuser(
            username="admin",
            password="adminadmin",
            email="admin@example.com")
        self.client = Client()
        self.client.force_login(user=self.user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
