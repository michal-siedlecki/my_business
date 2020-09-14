from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse

from apps.products.models import Product
from apps.invoices.models import Invoice
from mybusiness import factories


class InvoiceModelTests(TestCase):

    def setUp(self):
        self.user = factories.create_user()
        self.client.force_login(user=self.user)
        factories.update_user_profile(self.user)
        self.invoice = factories.create_invoice(1, self.user)

    def test_invoice_to_dict(self):
        pass


class InvoiceViewTest(TestCase):
    def setUp(self):
        self.user = factories.create_user()
        self.client.force_login(user=self.user)
        factories.update_user_profile(self.user)

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


