from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, Client

from apps.users.views import profile


class NotLoggedUserViewsTests(TestCase):

    def test_user_can_see_about_view(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "about")


class LoggedUserViewsTests(TestCase):
    def setUp(self):

        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def test_user_can_see_profile_view(self):

        request = self.factory.get('profile')
        request.user = self.user
        response = profile(request)

        self.assertEqual(response.status_code, 200)

    def test_user_can_see_dashboard_view(self):

        request = self.factory.get('dashboard')
        request.user = self.user
        response = profile(request)

        self.assertEqual(response.status_code, 200)

    def test_user_can_see_contractors_view(self):

        request = self.factory.get('contractors')
        request.user = self.user
        response = profile(request)

        self.assertEqual(response.status_code, 200)

    def test_user_can_see_contractors_new_view(self):

        request = self.factory.get('contractors-new')
        request.user = self.user
        response = profile(request)

        self.assertEqual(response.status_code, 200)

