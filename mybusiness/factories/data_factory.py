import datetime
from faker import Faker

faker = Faker('pl_PL')


def create_profile_data() -> dict:
    return {
        'company_name': faker.company(),
        'tin': faker.nip(),
        'bank_name': faker.credit_card_provider(),
        'bank_account_num': faker.random_number(26)
    }


def create_address_data() -> dict:
    return {
        'street': faker.street_address(),
        'city': faker.city(),
        'zip_code': faker.postcode()
    }


def create_user_data() -> dict:
    return {
        'username': faker.user_name(),
        'email': faker.email(),
        'password': faker.password()
    }


def create_bank_account_num() -> int:
    return faker.random_number(26)


def create_contractor_data() -> dict:
    return {
        'company_name': faker.company(),
        'tin': faker.nip()
    }


def create_product_data() -> dict:
    price_n = faker.random_int(10, 500)
    tax_r = faker.random_element([0, 8, 23])
    price_g = price_n+price_n*tax_r//100
    return {
        'product_id': faker.random_number(1),
        'name': f'produkt {faker.word()}',
        'price_nett': price_n,
        'price_gross': price_g,
        'tax_rate': tax_r,
    }


def create_invoice_product_data(product: dict) -> dict:
    quantity = faker.random_int(1, 90)
    total_nett = product.get('price_nett')*quantity
    total_tax = quantity*total_nett*product.get('tax_rate')//100
    total_gross = total_nett+total_tax
    product.update({
        'quantity': quantity,
        'prod_total_nett': total_nett,
        'prod_total_tax': total_tax,
        'prod_total_gross': total_gross
    })
    return product


def create_invoice_base_data() -> dict:
    date_created = datetime.datetime.strptime(faker.date(),'%Y-%m-%d').date()
    date_supply = date_created + datetime.timedelta(days=faker.random_int(0,3))
    date_due = date_created + datetime.timedelta(days=faker.random_int(7,30))
    return {
        'invoice_id': 'FV_'+str(faker.numerify()),
        'date_created': date_created,
        'city_created': faker.city(),
        'date_supply': date_supply,
        'date_due': date_due,
    }

