from django.contrib.auth.models import User
from apps.invoices.models import Invoice
from apps.products.models import Product
from apps.contractors.models import Contractor
from apps.users.models import Profile, Address

def get_user(pk):
    return User.objects.get(pk=pk)

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


def create_product(user, **data) -> Product:
    product = Product(**data)
    product.author = user
    product.full_clean()
    product.save()
    return product


def update_product(product_pk, data):
    Product.objects.filter(pk=product_pk).update(**data)


def create_invoice_product(user: str, invoice: Invoice, **data) -> Product:
    product = Product(**data)
    product.author = user
    product.document = invoice
    product.full_clean()
    product.save()
    return product


def create_contractor_from_user(user) -> Contractor:
    address = user.profile.address
    address.pk = None  # copy address
    address.save()
    contractor = Contractor.objects.create(
        company_name=user.profile.company_name,
        tin=user.profile.tin,
        address=address,
        author=user,
        on_invoice=True
    )
    contractor.save()
    return contractor


def create_contractor(data, address, user):
    address = Address.objects.create(**address)
    address.save()
    contractor = Contractor(
        **data,
        address=address,
        author=user
    )
    contractor.full_clean()
    contractor.save()


def update_contractor(contractor_pk, data, address_pk, address_data):
    Address.objects.filter(pk=address_pk).update(**address_data)
    Contractor.objects.filter(pk=contractor_pk).update(**data)


def copy_address(address):
    address.pk = None
    address.save()


def assign_contractor(contractor):
    contractor.pk = None  # to make a copy
    contractor_address = contractor.address
    contractor_address.pk = None
    contractor_address.save()
    contractor.address = contractor_address
    contractor.on_invoice = True
    contractor.save()
    return contractor


def assign_products_to_invoice(products, invoice):
    for product_data in products:
        product = Product(**product_data)
        product.document = invoice
        product.author = invoice.author
        product.save()


def create_invoice(invoice_data, user: User, buyer: Contractor) -> Invoice:
    invoice = Invoice(**invoice_data)
    profile = get_user_profile(user)
    copy_address(profile.address)  # copy seller address to avoid modification after
    invoice.seller = create_contractor_from_user(user)
    invoice.buyer = assign_contractor(buyer)
    invoice.author = user
    invoice.bank_num_account = profile.bank_account_num
    invoice.full_clean()
    invoice.save()
    return invoice


def update_invoice(invoice_pk, invoice_data) -> Invoice:
    Invoice.objects.filter(pk=invoice_pk).update(**invoice_data)
    invoice = Invoice.objects.get(pk=invoice_pk)
    return invoice


def create_profile(data, address, user):
    address = Address.objects.create(**address)
    address.save()
    profile = Profile(
        **data,
        address=address,
        user=user
    )
    profile.full_clean()
    profile.save()


def update_profile(profile_pk, data, address_pk, address_data):
    Address.objects.filter(pk=address_pk).update(**address_data)
    Profile.objects.filter(pk=profile_pk).update(**data)


def get_products_total_nett(products):
    sum = 0
    for product in products:
        sum += product.prod_total_nett
    return sum


def get_products_total_tax(products):
    sum = 0
    for product in products:
        sum += product.prod_total_tax
    return sum


def get_products_total_gross(products):
    sum = 0
    for product in products:
        sum += product.prod_total_gross
    return sum


def get_nett_tax_gross(nett: float, tax: float) -> dict:
    tax_value = nett * tax // 100
    gross = nett + tax_value
    return {
        'prod_total_nett': nett,
        'prod_total_tax': tax_value,
        'prod_total_gross': gross
    }


def get_nett_tax_gross_from_product_data(product_data: dict, quantity: int=None) -> dict:
    nett = product_data.get('price_nett')
    tax = product_data.get('tax_rate')
    if quantity:
        return {k: quantity*v for k,v in get_nett_tax_gross(nett, tax).items()}
    return get_nett_tax_gross(nett, tax)
