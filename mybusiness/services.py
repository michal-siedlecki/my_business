from django.contrib.auth.models import User
from apps.invoices.models import Invoice
from apps.products.models import Product
from apps.contractors.models import Contractor
from apps.users.models import Profile


def get_invoice_model():
    return Invoice


def get_contractor(pk):
    return Contractor.objects.get(pk=pk)


def get_user_profile(user: User) -> Profile:
    return Profile.objects.get(user=user)


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


def create_contractor_from_user(user: User) -> Contractor:
    profile = get_user_profile(user)
    address = profile.address
    address.pk = None
    address.save()
    contractor = Contractor(
        company_name=profile.company_name,
        tin=profile.tin,
        address=address,
        author=user,
        on_invoice=True
    )
    return contractor


def create_invoice(user: User, buyer: Contractor, **data) -> Invoice:
    invoice = Invoice(**data)
    profile = get_user_profile(user)
    address = profile.address
    address.pk = None
    address.save()
    invoice.buyer = buyer
    invoice.author = user
    invoice.bank_num_account = profile.bank_account_num
    invoice.seller = Contractor(
        company_name=profile.company_name,
        tin=profile.tin,
        address=address,
        author=user,
        on_invoice=True
    )
    invoice.full_clean()
    invoice.save()
    return invoice




