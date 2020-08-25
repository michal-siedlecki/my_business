from django.http import QueryDict
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse

from apps.products.models import Product
from apps.invoices.models import Invoice
from apps.users.models import Profile
from apps.contractors.models import Contractor
from mybusiness import serializers
from . import factories


class NotLoggedUserViewsTests(TestCase):
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


class LoggedUserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = factories.create_user()
        self.client.force_login(user=self.user)
        factories.update_user_profile(user=self.user)

    def test_user_profile_is_auto_created(self):
        user_profile = Profile.objects.get(user=self.user)

        self.assertEqual(user_profile.user, self.user)

    def test_logged_user_can_see_profile_view(self):
        url = reverse('profile')
        response = self.client.get(url)
        profile_data = Profile.objects.get(user=self.user)

        self.assertEqual(response.status_code, 200)
        for x in profile_data.to_list():
            self.assertContains(response, x)

    def test_user_can_update_profile(self):
        url = reverse('profile')
        profile_data = factories.create_profile_data()
        address_data = factories.create_address_data()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(profile_data)
        query_dict.update(address_data)
        response = self.client.post(url, query_dict)

        self.assertEqual(response.url, '/profile/')
        self.assertEqual(Profile.objects.get(user=self.user).company_name, profile_data.get('company_name'))

    def test_logged_user_can_see_invoice_list_view(self):
        url = (reverse('invoice-list'))
        factories.create_invoice(1, self.user, 5)
        response = self.client.get(url)
        invoices_in_view = response.context_data.get('object_list')
        invoices_of_user = Invoice.objects.filter(author=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            invoices_in_view.order_by('date_created'),
            map(repr, invoices_of_user)
        )

    def test_logged_user_can_see_invoice_create_view(self):
        url = (reverse('invoice-new'))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_invoice_detail_view(self):
        invoice = factories.create_invoice(1, self.user)
        url = (reverse('invoice-detail', kwargs={'pk': invoice.invoice_id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_logged_user_cant_see_other_users_invoices(self):
        other_user = factories.create_user()
        other_invoice = factories.create_invoice(1, other_user)
        url = (reverse('invoice-detail', kwargs={'pk': other_invoice.invoice_id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

        url = (reverse('invoice-update', kwargs={'pk': other_invoice.invoice_id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

        url = (reverse('invoice-delete', kwargs={'pk': other_invoice.invoice_id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_logged_user_can_see_invoice_update_view(self):
        invoice = factories.create_invoice(1, self.user)
        url = (reverse('invoice-update', kwargs={'pk': invoice.invoice_id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_contractor_create_view(self):
        url = (reverse('contractor-new'))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Create')

    def test_logged_user_can_see_contractor_update_view(self):
        contractor = factories.create_contractor(self.user)
        url = (reverse('contractor-update', kwargs={'pk': contractor.id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Update')

    def test_logged_user_can_see_product_create_view(self):
        url = (reverse('product-new'))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Create')

    def test_logged_user_can_see_product_update_view(self):
        product = factories.create_product(self.user)
        url = (reverse('product-update', kwargs={'pk': product.id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Update')

    def test_logged_user_can_see_contractor_list_view(self):
        factories.create_contractor(self.user)
        url = (reverse('contractor-list'))
        response = self.client.get(url)
        contractors_in_view = response.context_data.get('contractors')
        contractors_of_user = Contractor.objects.filter(author=self.user, on_invoice=False)

        self.assertEqual(len(contractors_in_view), len(contractors_of_user))
        self.assertEqual(response.status_code, 200)


class InvoiceCRUDTests(TestCase):

    def setUp(self):
        self.user = factories.create_user()
        self.client.force_login(user=self.user)
        factories.update_user_profile(self.user)

    def test_user_can_create_invoice_single_product(self):
        url = reverse('invoice-new')
        invoice_product_data = factories.create_invoice_product_data('sample_product')
        invoice_data = factories.create_invoice_data(self.user)
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
        url = reverse('invoice-new')
        invoice_product_data_01 = factories.create_invoice_product_data('sałata')
        invoice_product_data_02 = factories.create_invoice_product_data('ziemniak')
        invoice_data = factories.create_invoice_data(self.user)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(invoice_data)
        query_dict.update(invoice_product_data_01)
        query_dict.update(invoice_product_data_02)
        response = self.client.post(url, query_dict)

        self.assertEqual(response.status_code, 302)  # After invoice create it should redirect to invoice list
        self.assertEqual(response.url, '/invoices/')
        self.assertEqual(len(Invoice.objects.all()), 1)

    def test_user_can_update_invoice_loads_view(self):
        invoice = factories.create_invoice('FV_01', self.user)
        invoice.save()
        product_on_invoice = factories.create_invoice_product(document=invoice, author=self.user)
        product_on_invoice.save()
        url = (reverse('invoice-update', kwargs={'pk': invoice.pk}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_user_can_update_invoice_data(self):
        invoice = factories.create_invoice('FV_01', self.user)
        invoice.save()
        product_on_invoice = factories.create_invoice_product(document=invoice, author=self.user)
        product_on_invoice.save()
        url = (reverse('invoice-update', kwargs={'pk': invoice.pk}))
        updated_invoice_data = factories.create_invoice_data(self.user)
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
        self.user = factories.create_user()
        self.client.force_login(user=self.user)

    def test_user_can_see_create_product_view(self):
        url = (reverse('product-new'))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_user_can_create_product(self):
        product = factories.create_product_data()
        url = reverse('product-new')
        response = self.client.post(url, product)

        self.assertEqual(response.url, '/products')
        self.assertEqual(len(Product.objects.all()), 1)

    def test_user_can_create_invoice_product(self):
        product = factories.create_invoice_product_data('sample')
        url = reverse('product-new')
        response = self.client.post(url, product)

        self.assertEqual(response.url, '/products')
        self.assertEqual(len(Product.objects.all()), 1)


class ContractorCRUDTests(TestCase):
    def setUp(self) -> None:
        self.user = factories.create_user()
        self.client.force_login(user=self.user)
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


class SerializersTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = factories.create_user()
        self.client.force_login(user=self.user)
        self.product_1 = factories.create_invoice_product_data('sample_one')
        self.product_2 = factories.create_invoice_product_data('sample_two')
        self.invoice = factories.create_invoice_data(self.user)

    def test_product_serializer_returns_list(self):
        d = dict(self.invoice)
        d.update(self.product_1)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(d)
        query_dict.update(self.product_2)
        serializer = serializers.ProductInvoiceSerializer(data=query_dict)

        self.assertEqual(len(serializer.get_list()), 2)

