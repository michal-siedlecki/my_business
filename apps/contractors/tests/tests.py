from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse

from .models import Contractor
from mybusiness import factories


class ContractorModelTests(TestCase):
    def setUp(self) -> None:
        self.user = factories.create_user()
        self.client.force_login(user=self.user)
        self.contractor_data = factories.create_contractor_data()
        self.address_data = factories.create_address_data()
        factories.create_contractor(
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
        self.user = factories.create_user()
        self.client.force_login(user=self.user)
        self.contractor_data = factories.create_contractor_data()
        self.address_data = factories.create_address_data()

    def test_user_can_see_contractor_list(self):
        pass


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
        contractor = factories.create_contractor(self.user)
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


class ContractorSerializerTests(TestCase):
    pass



