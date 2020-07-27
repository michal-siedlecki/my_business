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


def create_product(user, **data) -> Product:
    product = Product(**data)
    product.author = user
    product.full_clean()
    product.save()
    return product


def create_invoice_product(user: str, invoice: Invoice, **data) -> Product:
    product = Product(**data)
    product.author = user
    product.document = invoice
    product.full_clean()
    product.save()
    return product


def create_invoice(user: str, **data) -> Invoice:
    invoice = Invoice(**data)
    invoice.author = user
    invoice.full_clean()
    invoice.save()
    return invoice
