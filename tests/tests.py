from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from apps.users.views import profile


class ProfileViewTests(TestCase):
    def setUp(self):

        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def test_user_can_see_profile_view(self):

        request = self.factory.get('profile')
        request.user = self.user
        response = profile(request)

        self.assertEqual(response.status_code, 200)
