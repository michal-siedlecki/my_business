from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, View
from django_weasyprint import WeasyTemplateResponseMixin

from mybusiness import services, serializers
from apps.products.forms import ProductInvoiceSerializer, ProductInvoiceForm
from .forms import InvoiceForm

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
    model = services.get_invoice_model()
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

    def post(self, request, *args, **kwargs):
        user = self.request.user
        buyer = services.get_contractor(request.POST.get('buyer'))
        invoice_serializer = serializers.InvoiceSerializer(data=request.POST)
        product_serializer = ProductInvoiceSerializer(data=request.POST)
        products = product_serializer.get_list()
        serialized_products = ProductInvoiceSerializer(data=products, many=True)
        serialized_products.is_valid(raise_exception=True)
        invoice_serializer.is_valid(raise_exception=True)
        services.create_invoice(
            invoice_data=invoice_serializer.validated_data,
            products=serialized_products.validated_data,
            user=user,
            buyer=buyer
        )
        messages.success(request, 'Invoice created')
        return redirect('invoice-list')


class InvoiceUpdateView(InvoiceCreateView, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = services.get_invoice_model()

    def get_context_data(self):
        user = self.request.user
        products = services.get_user_products(user)
        invoice = self.get_object()
        invoice_form = InvoiceForm(instance=invoice, user=user, buyer=invoice.buyer)
        products_on_invoice = serializers.serialize_products_on_invoice(invoice)

        context = {
            'invoice_form': invoice_form,
            'product_form': self.product_form,
            'products': products,
            'invoice_products': products_on_invoice,
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
        buyer = old_invoice.buyer
        invoice_serializer = serializers.InvoiceSerializer(data=request.POST)
        product_serializer = ProductInvoiceSerializer(data=request.POST)
        products = product_serializer.get_list()
        serialized_products = ProductInvoiceSerializer(data=products, many=True)
        serialized_products.is_valid(raise_exception=True)
        invoice_serializer.is_valid(raise_exception=True)
        services.create_invoice(
            invoice_data=invoice_serializer.validated_data,
            products=serialized_products.validated_data,
            user=user,
            buyer=buyer
        )
        messages.success(request, 'Invoice updated')
        return redirect('invoice-list')


class InvoiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = services.get_invoice_model()
    success_url = '/invoices/'

    def test_func(self):
        invoice = self.get_object()
        return self.request.user == invoice.author
