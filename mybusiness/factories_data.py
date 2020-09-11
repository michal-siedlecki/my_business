import json
from faker import Faker

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


def create_user_data():
    return {
        'username': faker.user_name(),
        'email': faker.email(),
        'password': faker.password()
    }


def create_bank_account_num():
    return faker.random_number(26)


def create_contractor_data():
    return {
        'company_name': faker.company(),
        'tin': faker.nip()
    }


def create_product_data():
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


def create_invoice_product_data(self):
    base = self.create_product_data()
    base.update({
        'quantity': 2,
        'prod_total_nett': 200,
        'prod_total_tax': 24,
        'prod_total_gross': 224
    })
    return base


def make_products_json(num):
    products = {'products': []}

    for num in range(num):
        product = create_product_data()
        product['product_id'] = num+1
        products.get('products').append(product)
    products_json = json.dumps(products)

    return products_json




def make_products_json(num):
    products = {'products': []}

    for num in range(num):
        product = create_product_data()
        product['product_id'] = num+1
        products.get('products').append(product)
    products_json = json.dumps(products)

    return products_json