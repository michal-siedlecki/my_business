from django.http import QueryDict
from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import fields


from apps.users.models import Profile, Address
from mybusiness.factories import model_factory


def get_to_list_fields(model):
    return list(field for field in model._meta.get_fields() if (
            not isinstance(field, fields.AutoField)
            and not isinstance(field, fields.reverse_related.OneToOneRel)
            and not isinstance(field, fields.related.OneToOneField)
    ))

class AddressModelTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = model_factory.create_user()
        self.client.force_login(user=self.user)
        self.address = self.user.profile.address

    def test_default_address_exists(self):
        self.assertIsNotNone(self.address)

    def test_address_to_list(self):
        address_list_fields = get_to_list_fields(Address)
        address_list = self.address.to_list()
        self.assertIs(isinstance(address_list, list), True)
        self.assertEqual(len(address_list), len(address_list_fields))


class ProfileModelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = model_factory.create_user()
        self.client.force_login(user=self.user)
        model_factory.update_fake_user_profile(user=self.user)

    def test_user_profile_is_auto_created(self):
        user_profile = Profile.objects.get(user=self.user)
        self.assertEqual(user_profile.user, self.user)

    def test_profile_to_list(self):
        list_fields = get_to_list_fields(Address)
        list_fields.append(get_to_list_fields(Profile))
        print(list_fields)

        profile_list = self.user.profile.to_list()
        self.assertIs(isinstance(profile_list, list), True)
        self.assertEqual(len(profile_list), len(list_fields))


class UnlogedUserViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_not_logged_user_can_see_about_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'about')

    def test_not_logged_user_can_see_login_view(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_not_logged_user_cant_see_invoices(self):
        response = self.client.get('/invoices/')
        self.assertEqual(response.status_code, 302)  # test if user is redirect to login
        self.assertEqual(response.url, '/login/?next=/invoices/')


class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = model_factory.create_user()
        self.client.force_login(user=self.user)
        model_factory.update_fake_user_profile(user=self.user)


    def test_logged_user_can_see_profile_view(self):
        url = reverse('profile')
        response = self.client.get(url)
        profile_data = Profile.objects.get(user=self.user)
        self.assertEqual(response.status_code, 200)
        for x in profile_data.to_list():
            self.assertContains(response, x)

    def test_user_can_update_profile(self):
        url = reverse('profile')
        profile_data = model_factory.create_profile_data()
        address_data = model_factory.create_address_data()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(profile_data)
        query_dict.update(address_data)
        response = self.client.post(url, query_dict)
        self.assertEqual(response.url, '/profile/')
        self.assertEqual(Profile.objects.get(user=self.user).company_name, profile_data.get('company_name'))

class UserFormTests(TestCase):
    pass