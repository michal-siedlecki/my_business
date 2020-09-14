from django.http import QueryDict
from django.test import TestCase, Client
from django.urls import reverse

from apps.contractors.models import Contractor
from mybusiness.factories import model_factory, data_factory


class ContractorModelTests(TestCase):
    def setUp(self) -> None:
        self.user = model_factory.create_user()
        self.client.force_login(user=self.user)
        self.contractor_data = data_factory.create_contractor_data()
        self.address_data = data_factory.create_address_data()
        model_factory.create_contractor(
            author=self.user,
            data=self.contractor_data,
            address=self.address_data
        )
        self.contractor = Contractor.objects.get(author=self.user)

    def test_contractor_model_str(self):
        self.assertEqual(str(self.contractor), self.contractor_data.get('company_name'))

    def test_contractor_to_list(self):
        self.contractor_data.update(**self.address_data)
        for item in self.contractor.to_list():
            self.assertIn(item, self.contractor_data.values())


class ContractorViewTests(TestCase):
    def setUp(self) -> None:
        self.user = model_factory.create_user()
        self.client.force_login(user=self.user)
        self.contractor_data = data_factory.create_contractor_data()
        self.address_data = data_factory.create_address_data()

    def test_user_can_see_contractor_list_view(self):
        model_factory.create_contractor(self.user)
        url = (reverse('contractor-list'))
        response = self.client.get(url)
        contractors_in_view = response.context_data.get('contractors')
        contractors_of_user = Contractor.objects.filter(author=self.user, on_invoice=False)

        self.assertEqual(len(contractors_in_view), len(contractors_of_user))
        self.assertEqual(response.status_code, 200)

    def test_user_can_create_contractor(self):
        url = reverse('contractor-new')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.contractor_data)
        query_dict.update(self.address_data)
        response = self.client.post(url, query_dict)

        self.assertEqual(response.url, '/contractors')
        self.assertEqual(len(Contractor.objects.all()), 1)
        self.assertIsNotNone(Contractor.objects.get(author=self.user))

    def test_user_can_update_contractor(self):
        contractor = model_factory.create_contractor(self.user)
        updated_contractor_data = self.contractor_data
        updated_contractor_data['company_name'] = 'New name'
        url = reverse('contractor-update', kwargs={'pk': contractor.pk})
        query_dict = QueryDict('', mutable=True)
        query_dict.update(updated_contractor_data)
        query_dict.update(self.address_data)
        response = self.client.post(url, query_dict)

        self.assertEqual(response.url, '/contractors')
        self.assertEqual(Contractor.objects.get(pk=contractor.pk).company_name, 'New name')

    def test_user_can_delete_contractor(self):
        pass


class LoggedUserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = model_factory.create_user()
        self.client.force_login(user=self.user)
        model_factory.update_fake_user_profile(user=self.user)

    def test_logged_user_can_see_contractor_create_view(self):
        url = (reverse('contractor-new'))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Create')

    def test_logged_user_can_see_contractor_update_view(self):
        contractor = model_factory.create_contractor(self.user)
        url = (reverse('contractor-update', kwargs={'pk': contractor.id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Update')

    def test_logged_user_can_see_contractor_list_view(self):
        model_factory.create_contractor(self.user)
        url = (reverse('contractor-list'))
        response = self.client.get(url)
        contractors_in_view = response.context_data.get('contractors')
        contractors_of_user = Contractor.objects.filter(author=self.user, on_invoice=False)

        self.assertEqual(len(contractors_in_view), len(contractors_of_user))
        self.assertEqual(response.status_code, 200)


class ContractorFormTests(TestCase):
    pass


class ContractorSerializerTests(TestCase):
    pass



