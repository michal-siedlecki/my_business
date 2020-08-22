from django.http import QueryDict
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse

from apps.products.models import Product
from apps.invoices.models import Invoice
from apps.invoices.views import InvoiceListView
from apps.users.models import Profile
from apps.users.views import profile
from apps.contractors.models import Contractor
from mybusiness import serializers
from . import factories


class NotLoggedUserViewsTests(TestCase):

    def test_not_logged_user_can_see_about_view(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'about')

    def test_not_logged_user_can_see_login_view(self):
        client = Client()
        response = client.get('/login/')

        self.assertEqual(response.status_code, 200)


class UserCreateTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def test_user_profile_autocreation(self):
        user_profile = Profile.objects.get(user=self.user)
        self.assertEqual(user_profile.user, self.user)


class LoggedUserViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        address = factories.create_address()
        address.save()
        self.user.profile.address = address

    def test_logged_user_can_see_profile_view(self):
        request = self.factory.get('profile')
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 200)

    def test_user_can_update_profile(self):
        user = self.user
        self.client.force_login(user=user)
        url = reverse('profile')
        profile_data = factories.create_profile_data()
        address_data = factories.create_address_data()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(profile_data)
        query_dict.update(address_data)
        response = self.client.post(url, query_dict)
        self.assertEqual(response.url, '/profile/')
        self.assertEqual(Profile.objects.get(user=user).company_name, profile_data.get('company_name'))


    def test_logged_user_can_see_invoice_list_view(self):
        request = self.factory.get('invoices')
        request.user = self.user
        response = InvoiceListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_invoice_create_view(self):
        user = self.user
        self.client.force_login(user)
        url = (reverse('invoice-new'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_invoice_detail_view(self):
        user = self.user
        self.client.force_login(user=user)
        invoice = factories.create_invoice(1, self.user)
        url = (reverse('invoice-detail', kwargs={'pk': invoice.invoice_id}))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_invoice_update_view(self):
        user = self.user
        self.client.force_login(user=user)
        invoice = factories.create_invoice(1, user)
        url = (reverse('invoice-update', kwargs={'pk': invoice.invoice_id}))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_contractor_create_view(self):
        user = self.user
        self.client.force_login(user=user)
        url = (reverse('contractor-new'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Create')

    def test_logged_user_can_see_contractor_update_view(self):
        user = self.user
        self.client.force_login(user=user)
        contractor = factories.create_contractor(user)
        url = (reverse('contractor-update', kwargs={'pk': contractor.id}))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Update')

    def test_logged_user_can_see_product_create_view(self):
        user = self.user
        self.client.force_login(user=user)
        url = (reverse('product-new'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Create')

    def test_logged_user_can_see_product_update_view(self):
        user = self.user
        self.client.force_login(user=user)
        product = factories.create_product(user)
        url = (reverse('product-update', kwargs={'pk': product.id}))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Update')

    def test_logged_user_can_see_contractor_list_view(self):
        user = self.user
        self.client.force_login(user=user)
        factories.create_contractor(user)
        url = (reverse('contractor-list'))
        response = self.client.get(url)
        contractors_in_view = response.context_data.get('contractors')
        contractors_of_user = Contractor.objects.filter(author=user, on_invoice=False)
        self.assertEqual(len(contractors_in_view), len(contractors_of_user))
        self.assertEqual(response.status_code, 200)


class InvoiceCRUDTests(TestCase):

    def setUp(self):
        self.user = factories.create_user()
        factories.update_user_profile(self.user)

    def test_user_can_create_invoice_single_product(self):
        user = self.user
        self.client.force_login(user=user)
        url = reverse('invoice-new')
        invoice_product_data = factories.create_invoice_product_data('sample_product')
        invoice_data = factories.create_invoice_data(user)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(invoice_data)
        query_dict.update(invoice_product_data)
        response = self.client.post(url, query_dict)
        invoice = Invoice.objects.first()
        self.assertEqual(response.url, '/invoices/')
        self.assertEqual(len(Invoice.objects.all()), 1)
        self.assertEqual(len(Product.objects.all()), 1)
        self.assertEqual(Product.objects.get(document=invoice).document, invoice)

    def test_user_can_create_invoice_multiple_product(self):
        user = self.user
        self.client.force_login(user=user)
        url = reverse('invoice-new')
        invoice_product_data_01 = factories.create_invoice_product_data('sałata')
        invoice_product_data_02 = factories.create_invoice_product_data('ziemniak')
        invoice_data = factories.create_invoice_data(user)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(invoice_data)

        query_dict2 = QueryDict('', mutable=True)
        query_dict2.update(invoice_product_data_01)

        query_dict3 = QueryDict('', mutable=True)
        query_dict3.update(invoice_product_data_02)

        q = {**query_dict, **query_dict2, **query_dict3}
        response = self.client.post(url, q)
        print(len(Product.objects.filter(author=user)))
        self.assertEqual(response.status_code, 302)  # After invoice create it should redirect to invoice list
        self.assertEqual(response.url, '/invoices/')
        self.assertEqual(len(Invoice.objects.all()), 1)

    def test_user_can_update_invoice_loads_view(self):
        user = self.user
        self.client.force_login(user=user)
        invoice = factories.create_invoice('FV_01', user)
        invoice.save()
        product_on_invoice = factories.create_invoice_product(document=invoice, author=user)
        product_on_invoice.save()
        url = (reverse('invoice-update', kwargs={'pk': invoice.pk}))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_can_update_invoice_data(self):
        user = self.user
        self.client.force_login(user=user)
        invoice = factories.create_invoice('FV_01', user)
        invoice.save()
        product_on_invoice = factories.create_invoice_product(document=invoice, author=user)
        product_on_invoice.save()
        url = (reverse('invoice-update', kwargs={'pk': invoice.pk}))
        updated_invoice_data = factories.create_invoice_data(user)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(updated_invoice_data)
        updated_product_data = factories.create_product_data()
        query_dict.update(updated_product_data)
        response = self.client.post(url, query_dict)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/invoices/')
        self.assertEqual(Invoice.objects.get(pk=1).invoice_id, updated_invoice_data.get('invoice_id'))


class ProductCRUDTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        self.client.force_login(user=self.user)

    def test_user_can_see_create_product_view(self):
        user = self.user
        self.client.force_login(user=user)
        url = (reverse('product-new'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_can_create_product(self):
        user = self.user
        self.client.force_login(user=user)
        product = factories.create_product_data()
        url = reverse('product-new')
        response = self.client.post(url, product)
        self.assertEqual(response.url, '/products')
        self.assertEqual(len(Product.objects.all()), 1)

    def test_user_can_create_invoice_product(self):
        user = self.user
        self.client.force_login(user=user)
        product = factories.create_invoice_product_data('sample')
        url = reverse('product-new')
        response = self.client.post(url, product)
        self.assertEqual(response.url, '/products')
        self.assertEqual(len(Product.objects.all()), 1)


class SerializersTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        user = self.user
        self.client.force_login(user=user)
        self.product_1 = factories.create_invoice_product_data('sample_one')
        self.product_2 = factories.create_invoice_product_data('sample_two')
        self.invoice = factories.create_invoice_data(user)

    def test_product_serializer_returns_list(self):
        d = dict(self.invoice)
        d.update(self.product_1)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(d)
        query_dict.update(self.product_2)
        serializer = serializers.ProductInvoiceSerializer(data=query_dict)
        self.assertEqual(len(serializer.get_list()), 2)


class ContractorCRUDTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        user = self.user
        self.client.force_login(user=user)
        self.contractor_data = factories.create_contractor_data()
        self.address_data = factories.create_address_data()

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
