import datetime
from django.contrib.auth.models import User

from apps.contractors.models import Contractor
from apps.invoices.models import Invoice
from apps.users.models import Address
from apps.products.models import Product


def create_address():
    return Address.objects.create(
        street='Example Street',
        city='Example',
        zip_code='00-123'
    )


def create_user():
    return User.objects.create_user(
        username='jacob',
        email='jacob@…',
        password='top_secret'
    )


def create_bank_account_num():
    return 2211112222333344445555


def update_user_profile(user):
    user.profile.address = create_address()
    user.profile.bank_account_num = create_bank_account_num()


def create_invoice(invoice_id, author):
    return Invoice.objects.create(
        invoice_id=invoice_id,
        author=author
    )


def create_invoice_product(document, author):
    return Product(
        **create_product_data(),
        document=document,
        author=author
    )


def create_contractor(author):
    return Contractor.objects.create(
        company_name='Sample C.o.',
        tin=123456789,
        address=create_address(),
        author=author,
        on_invoice=False
    )


def create_invoice_data(author):
    return {
        'invoice_id': 1,
        'date_created': datetime.date(2020, 8, 5),
        'city_created': 'Sample City',
        'seller': create_contractor(author=author).id,
        'buyer': create_contractor(author=author).id,
        'total_nett': 200.0,
        'total_tax': 48.0,
        'total_gross': 248.0,
        'bank_num_account': '2255550000111122223333',
        'date_supply': datetime.date(2020, 8, 5),
        'date_due': datetime.date(2020, 8, 5),
        'author': author
    }


def create_product_data():
    return {
        'product_id': 1,
        'name': 'sample_product',
        'price_nett': 100,
        'price_gross': 123,
        'tax_rate': 23,
    }


def create_invoice_product_data(name):
    return {
        'product_id': 1,
        'name': name,
        'price_nett': 100,
        'price_gross': 123,
        'tax_rate': 23,
        'quantity': 2,
        'prod_total_nett': 200,
        'prod_total_tax': 24,
        'prod_total_gross': 224
    }
