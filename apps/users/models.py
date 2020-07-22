from django.apps import apps
from django.contrib.auth.models import User
from django.db import models


class Address(models.Model):
    street = models.CharField(max_length=100, default='')
    city = models.CharField(max_length=100, default='')
    zip_code = models.CharField(max_length=100, default='')

    def to_list(self):
        city_zip = " ".join([self.city, str(self.zip_code)])
        return [self.street, city_zip]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, default='')
    tin = models.CharField(max_length=100, default='')
    bank_name = models.CharField(max_length=100, default='')
    bank_account_num = models.CharField(max_length=26, default='')
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.company_name

    def to_list(self):
        return [self.company_name, *self.address.to_list(), str("NIP: " + str(self.tin))]

    def make_contractor(self, author):
        contractor = apps.get_model('contractors', 'Contractor')
        address = self.address
        address.pk = None
        address.save()
        return contractor(
            company_name=self.company_name,
            tin=self.tin,
            address=address,
            author=author,
            on_invoice=True
        )
