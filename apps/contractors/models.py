from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from apps.users.models import Address


class Contractor(models.Model):
    company_name = models.CharField(max_length=100)
    tin = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    on_invoice = models.BooleanField(default=False)

    @staticmethod
    def get_absolute_url():
        return reverse('contractor-list')

    def __str__(self):
        return self.company_name

    def to_list(self):
        return [self.company_name, *self.address.to_list(), str("NIP: " + str(self.tin))]

    def copy(self, author):
        new_contractor = self
        new_contractor.pk = None
        address = self.address
        address.pk = None
        address.save()
        new_contractor.address = address
        new_contractor.author = author
        new_contractor.on_invoice = True
        return new_contractor
