import datetime
from faker import Faker
from django.contrib.auth.models import User

from apps.contractors.models import Contractor
from apps.invoices.models import Invoice
from apps.users.models import Address, Profile
from apps.products.models import Product

faker = Faker('pl_PL')


def create_profile_data():
    return {
        'company_name': faker.company(),
        'tin': faker.nip(),
        'bank_name': faker.credit_card_provider(),
        'bank_account_num': faker.random_number(26)
    }


def create_address_data():
    return {
        'street': faker.street_address(),
        'city': faker.city(),
        'zip_code': faker.postcode()
    }


def create_address():
    return Address.objects.create(**create_address_data())


def create_user():
    return User.objects.create_user(
        username=faker.user_name(),
        email=faker.email(),
        password=faker.password()
    )


def create_bank_account_num():
    return faker.random_number(26)


def update_user_profile(user):
    user.profile.address = create_address()
    user.profile.address.save()
    profile_data = create_profile_data()
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
        'bank_num_account': create_bank_account_num(),
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


def create_contractor_data():
    return {
        'company_name': faker.company(),
        'tin': faker.nip()
    }


def create_contractor(author):
    return Contractor.objects.create(
        **create_contractor_data(),
        address=create_address(),
        author=author,
        on_invoice=False
    )


def create_product_data():
    return {
        'product_id': faker.random_number(1),
        'name': 'sample_product',
        'price_nett': 100,
        'price_gross': 123,
        'tax_rate': 23,
    }


def create_invoice_product_data(name):
    base = create_product_data()
    base.update({
        'quantity': 2,
        'prod_total_nett': 200,
        'prod_total_tax': 24,
        'prod_total_gross': 224
    })
    return base


def create_product(user):
    return Product.objects.create(**create_product_data(), author=user)
