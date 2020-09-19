import random

from mybusiness import services
from . import model_factory

USERS_NUM = [15,20]
PRODUCTS_PER_USER = [10,30]
CONTRACTORS_PER_USER = [10,100]
INVOICES_PER_USER = [12,200]
PRODUCTS_ON_INVOICE = [1,10]


class Creator():

    def __init__(self):
        self.users_num = random.randint(*USERS_NUM)
        self.users = []
        self.products = []
        self.invoice_products = []
        self.contractors = []

    def create_users(self):
        for _ in range(self.users_num):
            user = model_factory.create_user()
            model_factory.update_fake_user_profile(user)
            self.users.append(user)

    def create_products(self, author):
        product_num = random.randint(*PRODUCTS_PER_USER)
        for _ in range(product_num):
            model_factory.create_product(author=author)

    def create_contractors(self, author):
        contractors_num = random.randint(*CONTRACTORS_PER_USER)
        for _ in range(contractors_num):
            model_factory.create_contractor(author=author)

    def create_invoices(self, author):
        invoices_num = random.randint(*INVOICES_PER_USER)
        for _ in range(invoices_num):
            model_factory.create_fake_invoice(author=author)

    def create_data(self):
        self.create_users()
        for user in self.users:
            self.create_products(author=user)
            self.create_contractors(author=user)
            self.create_invoices(author=user)

