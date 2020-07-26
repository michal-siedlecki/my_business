from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import ProductForm
from .models import Product
from mybusiness import services


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

    def form_valid(self, form):
        form.instance.author = self.request.user
        return form

    def post(self, request, *args, **kwargs):
        form = ProductForm(data=request.POST, instance=Product())
        if form.is_valid():
            product = self.form_valid(form).save(commit=False)
            product.save()
            messages.success(request, f'Product created')
            return redirect('product-list')
        return redirect('product-new')


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
        form = ProductForm(data=request.POST, instance=self.get_object())
        if form.is_valid():
            product = self.form_valid(form).save(commit=False)
            product.save()
            messages.success(request, f'Product created')
            return redirect('product-list')
        return redirect('product-new')


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
