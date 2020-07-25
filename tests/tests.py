from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse

from apps.invoices.models import Invoice
from apps.users.views import profile
from apps.invoices.views import InvoiceListView, InvoiceCreateView


class NotLoggedUserViewsTests(TestCase):

    def test_not_logged_user_can_see_about_view(self):
        client = Client()
        response = client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'about')


class LoggedUserViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')

    def create_invoice(self, invoice_id, author):
        """
        Create an invoice with the given `invoice_id`.
        """
        return Invoice.objects.create(invoice_id=invoice_id, author=author)

    def test_logged_user_can_see_profile_view(self):
        request = self.factory.get('profile')
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_invoice_list_view(self):
        request = self.factory.get('invoices')
        request.user = self.user
        response = InvoiceListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_invoice_create_view(self):
        request = self.factory.get('invoice-new')
        request.user = self.user
        response = InvoiceCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_invoice_detail_view(self):
        self.client.force_login(user=self.user)
        invoice = self.create_invoice(1, self.user)
        url = (reverse('invoice-detail', kwargs={'pk': invoice.invoice_id}))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class BusinessLogicTests(TestCase):
    pass