from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import ProductForm
from .models import Product
from mybusiness import services, serializers


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_form.html'
    success_url = '/products'
    form_class = ProductForm

    def get_context_data(self, **kwargs):
        context = {
            'form': self.form_class,
            'submit_button': 'Create'
        }
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = serializers.ProductSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)
        services.create_product(**serializer.validated_data, user=user)
        messages.success(request, 'Product created')
        return redirect('product-list')


class ProductUpdateView(ProductCreateView, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product

    def get_context_data(self, **kwargs):
        context = {
            'form': self.form_class(instance=self.get_object()),
            'submit_button': 'Update'
        }
        return context

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.author

    def post(self, request, *args, **kwargs):
        product_pk = self.get_object().pk
        serializer = serializers.ProductSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)
        services.update_product(data=serializer.validated_data, product_pk=product_pk)
        messages.success(request, 'Product updated')
        return redirect('product-list')


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        products = services.get_user_products(self.request.user)
        return products


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    success_url = '/products'

    def test_func(self):
        product = self.get_object()
        return self.request.user == product.author
