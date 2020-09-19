from faker import Faker
from django.contrib.auth.models import User

from apps.contractors.models import Contractor
from apps.invoices.models import Invoice
from apps.users.models import Address
from apps.products.models import Product
from mybusiness.factories import data_factory as fd
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
    user.profile.bank_name = profile_data.get('bank_name')
    user.profile.bank_account_num = profile_data.get('bank_account_num')
    user.profile.save()


def create_fake_invoice(author, data=None, buyer=None, products=None):
    invoice = Invoice(**data) if data else Invoice()
    invoice.author = author
    if not buyer:
        buyer = create_contractor(author=author)
    if not products:
        products = [create_product(author=author)]
    invoice.total_nett = services.get_products_total_nett(products)
    invoice.total_tax = services.get_products_total_tax(products)
    invoice.total_gross = services.get_products_total_gross(products)
    invoice.buyer = buyer
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


def create_product(author):
    return Product.objects.create(**fd.create_product_data(), author=author)


def create_invoice_product(document, author_id, product=None):
    base_product_data = fd.create_product_data()
    author = services.get_user(author_id)
    quantity = faker.random_int(1,99)
    product_summary = services.get_nett_tax_gross_from_product_data(base_product_data, quantity=quantity)
    product = Product(
        **base_product_data,
        **product_summary,
        document=document
    )
    product.author = author
    product.save()
    return product


def create_invoice_products(document, author, products: list):
    return map(create_invoice_product(document, author), products)


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



