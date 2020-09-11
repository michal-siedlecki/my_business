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


def create_invoice_product_data(product):
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


def make_products(num):
    products = {'products': []}

    for num in range(num):
        product = create_product_data()
        product['product_id'] = num+1
        products.get('products').append(product)

    return products


def make_invoice_products(products):
    invoice_products = {'invoice_products': []}

    for num, product in enumerate(products.get('products')):
        invoice_product = create_invoice_product_data(product)
        invoice_product['product_id'] = num+1
        invoice_products.get('invoice_products').append(invoice_product)

    return invoice_products


def save_obj(obj, filename):
    obj_json = json.dumps(obj)
    with open(filename, 'w') as f:
        f.write(obj_json)


p = make_products(10)
ip = make_invoice_products(p)

for item in ip['invoice_products']:
    print(item)
    print()

