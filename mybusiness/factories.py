import datetime
from faker import Faker
from django.contrib.auth.models import User

from apps.contractors.models import Contractor
from apps.invoices.models import Invoice
from apps.users.models import Address
from apps.products.models import Product
from mybusiness import factories_data as fd

faker = Faker('pl_PL')


def create_user():
    return User.objects.create_user(**fd.create_user_data())


def create_address(data=None):
    if data:
        return Address.objects.create(**data)
    return Address.objects.create(**fd.create_address_data())


def update_user_profile(user):
    user.profile.address = create_address()
    user.profile.address.save()
    profile_data = fd.create_profile_data()
    user.profile.company_name = profile_data.get('company_name')
    user.profile.tin = profile_data.get('tin')
    user.profile.save()


def create_invoice_data(author):
    return {
        'invoice_id': 'FV'+str(faker.numerify()),
        'date_created': datetime.date(2020, 8, 5),
        'city_created': faker.city(),
        'seller': create_contractor(author=author).id,
        'buyer': create_contractor(author=author).id,
        'total_nett': 200.0,
        'total_tax': 48.0,
        'total_gross': 248.0,
        'bank_num_account': fd.create_bank_account_num(),
        'date_supply': datetime.date(2020, 8, 5),
        'date_due': datetime.date(2020, 8, 5),
        'author': author,
        'prod_total_nett': 20,
        'prod_total_tax': 5,
        'prod_total_gross': 25
    }


def create_invoice(invoice_id, author, num=None):
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


def create_invoice_product(document, author):
    return Product(
        **create_product_data(),
        document=document,
        author=author
    )

def create_contractor(author, data=None, address=None):
    if not address:
        address=create_address()
    else:
        address=create_address(data=address)
    if data:
        return Contractor.objects.create(
            **data,
            author=author,
            address=address
        )
    return Contractor.objects.create(
        **create_contractor_data(),
        author=author,
        address=address
    )




def create_product(user):
    return Product.objects.create(**create_product_data(), author=user)

