from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import serializers
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django_weasyprint import WeasyTemplateResponseMixin

from apps.products.forms import ProductInvoiceForm
from apps.products.models import Product, ProductInvoice
from mybusiness import services
from .forms import InvoiceForm
from .models import Invoice


def about(request):
    return render(request, 'about.html', {'title': 'about'})


class InvoiceListView(LoginRequiredMixin, ListView):
    model = services.get_invoice_model()
    template_name = 'invoices/invoices.html'
    context_object_name = 'invoices'
    ordering = ['date_created']

    def get_queryset(self):
        user = self.request.user
        return services.get_user_invoices(user)


class InvoiceDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Invoice
    template_name = 'invoices/invoice_detail.html'

    def get_context_data(self, **kwargs):
        products = ProductInvoice.objects.filter(author=self.request.user, document=self.get_object())
        context = {
            'products': products,
            'invoice': self.get_object(),
            'detail_view': True
        }
        return context

    def test_func(self):
        invoice = self.get_object()
        return self.request.user == invoice.author


class InvoiceDownloadView(WeasyTemplateResponseMixin, InvoiceDetailView):
    pdf_stylesheets = [
        'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'
    ]

    def get_pdf_filename(self):
        invoice = InvoiceDetailView.get_object(self)
        return str(invoice.invoice_id)

    def get_context_data(self, **kwargs):
        context = InvoiceDetailView.get_context_data(self, **kwargs)
        context['detail_view'] = False
        return context


def get_products(request):
    values = (dict(request.POST.lists()))
    products_num = len(values.get('product_id'))
    products = []

    for i in range(products_num):
        product = {}
        for field in ProductInvoiceForm.base_fields:
            product[field] = values.get(field)[i]
        products.append(product)

    return products


class InvoiceCreateView(View):
    template_name = 'invoices/invoice_form.html'
    success_url = ''
    invoice_form = InvoiceForm
    product_form = ProductInvoiceForm

    def get_context_data(self):
        user = self.request.user
        products = services.get_user_products(user)

        context = {
            'invoice_form': self.invoice_form(user=user),
            'product_form': self.product_form,
            'products': products,
            'seller_data': self.request.user.profile
        }
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def invoice_form_valid(self, invoice_form):
        author = self.request.user
        seller_contractor = self.request.user.profile.make_contractor(author=author)
        seller_contractor.save()
        invoice_form.instance.seller = seller_contractor
        buyer_contractor = invoice_form.instance.buyer.copy(author=author)
        buyer_contractor.save()
        invoice_form.instance.buyer = buyer_contractor
        invoice_form.instance.author = author
        invoice_form.instance.bank_num_account = author.profile.bank_account_num
        return invoice_form

    def product_form_valid(self, product_form, invoice):
        product_form.instance.author = self.request.user
        product_form.instance.document = invoice
        return product_form

    def post(self, request, *args, **kwargs):
        invoice_form = InvoiceForm(data=request.POST, instance=Invoice(), user=self.request.user)
        products = get_products(request)
        product_forms = [ProductInvoiceForm(data=product) for product in products]
        if invoice_form.is_valid() and all([pf.is_valid() for pf in product_forms]):
            new_invoice = self.invoice_form_valid(invoice_form).save(commit=False)
            new_invoice.save()
            for product_form in product_forms:
                new_product = self.product_form_valid(product_form, new_invoice).save(commit=False)
                new_product.save()
            messages.success(request, 'Invoice created')
            return redirect('invoice-list')
        return redirect('invoice-new')


class InvoiceUpdateView(InvoiceCreateView, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Invoice

    def get_context_data(self):
        invoice = self.get_object()
        invoice_form = InvoiceForm(instance=invoice, user=self.request.user, buyer=invoice.buyer)
        json_serializer = serializers.get_serializer("json")()
        products = Product.objects.filter(author=self.request.user)
        invoice_products = json_serializer.serialize(
            ProductInvoice.objects.filter(author=self.request.user, document=invoice),
            ensure_ascii=False
        )

        context = {
            'invoice_form': invoice_form,
            'product_form': self.product_form,
            'products': products,
            'invoice_products': invoice_products,
            'seller_data': invoice.seller
        }

        return context

    def test_func(self):
        invoice = self.get_object()
        return self.request.user == invoice.author

    def post(self, request, *args, **kwargs):
        old_invoice = self.get_object()
        ProductInvoice.objects.filter(document=old_invoice).delete()
        invoice_form = InvoiceForm(
            data=request.POST,
            instance=self.get_object(),
            user=self.request.user,
            buyer=old_invoice.buyer)
        products = get_products(request)
        product_forms = [ProductInvoiceForm(data=product) for product in products]

        if invoice_form.is_valid() and all([pf.is_valid() for pf in product_forms]):
            new_invoice = self.invoice_form_valid(invoice_form).save(commit=False)
            new_invoice.save()
            for product_form in product_forms:
                new_product = self.product_form_valid(product_form, new_invoice).save(commit=False)
                new_product.save()
            messages.success(request, 'Invoice updated')
            return redirect('invoice-list')
        return redirect('invoice-new')


class InvoiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Invoice
    success_url = '/invoices/'

    def test_func(self):
        invoice = self.get_object()
        return self.request.user == invoice.author
