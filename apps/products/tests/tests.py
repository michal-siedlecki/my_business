from django.http import QueryDict
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse

from apps.products.models import Product
from mybusiness import serializers
from mybusiness.factories import data_factory, model_factory


class ProductModelTests(TestCase):
    pass


class ProductViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = model_factory.create_user()
        self.client.force_login(user=self.user)
        model_factory.update_fake_user_profile(user=self.user)

    def test_logged_user_can_see_product_create_view(self):
        url = (reverse('product-new'))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Create')

    def test_logged_user_can_see_product_update_view(self):
        product = model_factory.create_product(self.user)
        url = (reverse('product-update', kwargs={'pk': product.id}))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data.get('submit_button'), 'Update')

    def test_user_can_see_create_product_view(self):
        url = (reverse('product-new'))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_user_can_create_product(self):
        product = data_factory.create_product_data(author_id=self.user.pk)
        url = reverse('product-new')
        response = self.client.post(url, product)

        self.assertEqual(response.url, '/products')
        self.assertEqual(len(Product.objects.all()), 1)

    def test_user_can_create_invoice_product(self):
        product_data = data_factory.create_product_data(author_id=self.user.pk)
        product_invoice_data = data_factory.create_invoice_product_data(product_data)
        url = reverse('product-new')
        response = self.client.post(url, product_invoice_data)

        self.assertEqual(response.url, '/products')
        self.assertEqual(len(Product.objects.all()), 1)


class ProductFormTests(TestCase):
    pass


class ProductSerializerTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = model_factory.create_user()
        self.client.force_login(user=self.user)
        self.other_contractor = model_factory.create_contractor(author=self.user)
        product_data = data_factory.create_product_data(author_id=self.user.pk)
        self.product_1_data = data_factory.create_invoice_product_data(product_data)
        product_data = data_factory.create_product_data(author_id=self.user.pk)
        self.product_2_data = data_factory.create_invoice_product_data(product_data)
        self.invoice_data = data_factory.create_invoice_base_data(seller_pk=self.user.pk, buyer_pk=self.other_contractor.pk)

    def test_product_serializer_returns_list(self):
        d = self.invoice_data.copy()
        d.update(self.product_1_data)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(d)
        query_dict.update(self.product_2_data)
        serializer = serializers.ProductInvoiceSerializer(data=query_dict)

        self.assertEqual(len(serializer.get_list()), 2)
