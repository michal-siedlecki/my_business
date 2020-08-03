from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import serializers
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django_weasyprint import WeasyTemplateResponseMixin

from apps.products.forms import ProductInvoiceForm
from mybusiness import services
from apps.products.forms import ProductInvoiceSerializer
from .forms import InvoiceForm, InvoiceSerializer
from .models import Invoice

PDF_STYLESHEETS = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min']


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
        invoice = self.get_object()
        context = {
            'products': services.get_invoice_products(invoice),
            'invoice': invoice,
            'detail_view': True
        }
        return context

    def test_func(self):
        invoice = self.get_object()
        return self.request.user == invoice.author


class InvoiceDownloadView(WeasyTemplateResponseMixin, InvoiceDetailView):
    pdf_stylesheets = [
        'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min'
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


class InvoiceCreateView(LoginRequiredMixin, View):
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
            'seller_data': user.profile
        }
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def product_form_valid(self, product_form, invoice):
        product_form.instance.author = self.request.user
        product_form.instance.document = invoice
        return product_form

    def post(self, request, *args, **kwargs):
        user = self.request.user
        buyer = services.get_contractor(request.POST.get('buyer'))
        invoice_serializer = InvoiceSerializer(data=request.POST)
        product_serializer = ProductInvoiceSerializer(data=request.POST, many=True)
        product_serializer.is_valid(raise_exception=True)
        invoice_serializer.is_valid(raise_exception=True)
        services.create_invoice(
            invoice_data=invoice_serializer.validated_data,
            products=product_serializer,
            user=user,
            buyer=buyer
        )
        messages.success(request, 'Invoice created')
        return redirect('invoice-list')


class InvoiceUpdateView(InvoiceCreateView, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Invoice

    def get_context_data(self):
        user = self.request.user
        invoice = self.get_object()
        invoice_form = InvoiceForm(instance=invoice, user=user, buyer=invoice.buyer)
        json_serializer = serializers.get_serializer("json")()
        products = services.get_user_products(user)
        invoice_products = json_serializer.serialize(
            services.get_invoice_products(invoice),
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
        user = self.request.user
        old_invoice = self.get_object()
        services.get_invoice_products(old_invoice).delete()
        invoice_form = InvoiceForm(
            data=request.POST,
            instance=self.get_object(),
            user=user,
            buyer=old_invoice.buyer)
        products = get_products(request)
        product_forms = [ProductInvoiceForm(data=product) for product in products]

        if invoice_form.is_valid() and all([pf.is_valid() for pf in product_forms]):
            new_invoice = self.invoice_form.populate_form_fields(invoice_form, user).save(commit=False)
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
