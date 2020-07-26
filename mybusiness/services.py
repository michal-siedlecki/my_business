from apps.invoices.models import Invoice
from apps.products.models import Product


def get_invoice_model():
    return Invoice


def get_user_invoices(user):
    return Invoice.objects.filter(author=user)


def get_user_products(user):
    return Product.objects.filter(author=user, document=None)


def get_invoice_products(invoice):
    return Product.objects.filter(document=invoice)


def add_product_to_invoice(invoice, product):
    product(document=invoice)
    product.save()


