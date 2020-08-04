from django.http import QueryDict
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse

from apps.products.models import Product
from apps.products.forms import ProductInvoiceSerializer
from apps.invoices.models import Invoice
from apps.invoices.views import InvoiceListView, InvoiceCreateView
from apps.users.models import Profile, Address
from apps.users.views import profile


def create_invoice(invoice_id, author):
    return Invoice.objects.create(invoice_id=invoice_id, author=author)


def create_invoice_data():
    return {
        'invoice_id': 1
    }


def create_product():
    return {
        'product_id': 1,
        'name': 'sample_product',
        'price_nett': 100,
        'price_gross': 123,
        'tax_rate': 23,
    }


def create_address():
    return Address(
        street='Example Street',
        city='Example',
        zip_code='00-123'
    )




def create_invoice_product():
    return {
        'product_id': 1,
        'name': 'sample_product',
        'price_nett': 100,
        'price_gross': 123,
        'tax_rate': 23,
        'quantity': 2,
        'prod_total_nett': 200,
        'prod_total_tax': 24,
        'prod_total_gross': 224
    }


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

    def test_user_profile_creation(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)


class LoggedUserViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        address = create_address()
        address.save()
        self.user.profile.address = address

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
        invoice = create_invoice(1, self.user)
        url = (reverse('invoice-detail', kwargs={'pk': invoice.invoice_id}))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logged_user_can_see_update_invoice_view(self):
        user = self.user
        self.client.force_login(user=user)
        invoice = create_invoice(1, user)
        url = (reverse('invoice-update', kwargs={'pk': invoice.invoice_id}))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class InvoiceCRUDTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        address = create_address()
        address.save()
        self.user.profile.address = address

    # def test_user_can_create_invoice(self):
    #     user = self.user
    #     self.client.force_login(user=user)
    #     url = reverse('invoice-new')
    #     invoice_product = create_invoice_product()
    #     invoice = create_invoice(1, user)
    #     response = self.client.post(url, invoice)
    #     self.assertEqual(response.url, '/invoices')
    #     self.assertEqual(len(Invoice.objects.all()), 1)


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
        product = create_product()
        url = reverse('product-new')
        response = self.client.post(url, product)
        self.assertEqual(response.url, '/products')
        self.assertEqual(len(Product.objects.all()), 1)

    def test_user_can_create_invoice_product(self):
        user = self.user
        self.client.force_login(user=user)
        product = create_invoice_product()
        url = reverse('product-new')
        response = self.client.post(url, product)
        self.assertEqual(response.url, '/products')
        self.assertEqual(len(Product.objects.all()), 1)


class SerializerTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='jacob', email='jacob@…', password='top_secret')
        user = self.user
        self.client.force_login(user=user)
        self.product_1 = create_invoice_product()
        self.product_2 = create_invoice_product()
        self.invoice = create_invoice_data()

    def test_product_serializer_returns_list(self):
        d = dict(self.invoice)
        d.update(self.product_1)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(d)
        query_dict.update(self.product_2)
        serializer = ProductInvoiceSerializer(data=query_dict, many=True)
        print(serializer.child.is_valid())
        print(serializer.child.is_valid())


