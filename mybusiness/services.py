from django.contrib.auth.models import User
from apps.invoices.models import Invoice
from apps.products.models import Product
from apps.contractors.models import Contractor
from apps.users.models import Profile, Address


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


def create_address() -> Address:
    return Address(
        street='Example Street',
        city='Example',
        zip_code='00-123'
    )


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


def create_invoice(invoice_data, products, user: User, buyer: Contractor) -> Invoice:
    invoice = Invoice(**invoice_data)
    profile = get_user_profile(user)
    address = profile.address
    address.pk = None  # to make a copy
    address.save()
    invoice.seller = create_contractor_from_user(user)
    invoice.buyer = buyer
    invoice.author = user
    invoice.bank_num_account = profile.bank_account_num
    invoice.full_clean()
    invoice.save()
    for product_data in products:
        product = Product(**product_data)
        product.document = invoice
        product.author = user
        product.save()
    return invoice
