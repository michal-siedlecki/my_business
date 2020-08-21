from django.contrib.auth.models import User
from django.db import models


class Address(models.Model):
    street = models.CharField(max_length=100, default='UNDEFINED')
    city = models.CharField(max_length=100, default='UNDEFINED')
    zip_code = models.CharField(max_length=100, default='UNDEFINED')

    objects = models.Manager()

    def to_list(self):
        city_zip = " ".join([self.city, str(self.zip_code)])
        return [self.street, city_zip]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, default='UNDEFINED')
    tin = models.CharField(max_length=100, default='UNDEFINED')
    bank_name = models.CharField(max_length=100, default='UNDEFINED')
    bank_account_num = models.CharField(max_length=26, default='UNDEFINED')
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.company_name

    def to_list(self):
        return [self.company_name, *self.address.to_list(), str("NIP: " + str(self.tin))]

