from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from apps.invoices.models import Invoice


class Product(models.Model):
    product_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    price_nett = models.FloatField(default=0)
    price_gross = models.FloatField(default=0)
    tax_rate = models.FloatField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True, null=True)
    document = models.ForeignKey(Invoice, on_delete=models.CASCADE, blank=True, null=True)
    prod_total_nett = models.FloatField(default=0)
    prod_total_tax = models.FloatField(default=0)
    prod_total_gross = models.FloatField(default=0)

    objects = models.Manager()

    @staticmethod
    def get_absolute_url():
        return reverse('product-list')


