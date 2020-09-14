from faker import Faker
from django.contrib.auth.models import User

from apps.contractors.models import Contractor
from apps.invoices.models import Invoice
from apps.users.models import Address
from apps.products.models import Product
from mybusiness.tests import factories_data as fd
from mybusiness import services

faker = Faker('pl_PL')


def create_user(data: dict = None) -> User:
    if data:
        return User.objects.create(**data)
    return User.objects.create_user(**fd.create_user_data())


def create_fake_address(data: dict = None) -> Address:
    if data:
        return Address.objects.create(**data)
    return Address.objects.create(**fd.create_address_data())


def update_fake_user_profile(user):
    user.profile.address = create_fake_address()
    user.profile.address.save()
    profile_data = fd.create_profile_data()
    user.profile.company_name = profile_data.get('company_name')
    user.profile.tin = profile_data.get('tin')
    user.profile.save()


def create_fake_invoice(author, data=None, buyer=None, products=None):
    invoice = Invoice(**data) if data else Invoice()
    invoice.author = author
    invoice.total_nett = services.get_products_total_nett(products)
    invoice.total_tax = services.get_products_total_tax(products)
    invoice.total_gross = services.get_products_total_gross(products)
    invoice.buyer = buyer if buyer else create_contractor(author)
    invoice.save()
    services.assign_contractor(buyer)
    services.assign_products_to_invoice(products=products, invoice=invoice)
    return invoice


def create_empty_invoice(invoice_id, author, num=None):
    if num:
        for _ in range(num):
            Invoice.objects.create(
                invoice_id=invoice_id,
                author=author
            )
    else:
        return Invoice.objects.create(
            invoice_id=invoice_id,
            author=author
        )

def create_product(user):
    return Product.objects.create(**fd.create_product_data(), author=user)

def create_invoice_product(document, author):
    return Product(
        **fd.create_product_data(),
        document=document,
        author=author
    )

def create_contractor(author, data=None, address=None):
    if not address:
        address=create_fake_address()
    else:
        address=create_fake_address(data=address)
    if data:
        return Contractor.objects.create(
            **data,
            author=author,
            address=address
        )
    return Contractor.objects.create(
        **fd.create_contractor_data(),
        author=author,
        address=address
    )



