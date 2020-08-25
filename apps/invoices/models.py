from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.contractors.models import Contractor


class Invoice(models.Model):
    invoice_id = models.CharField(max_length=100)
    date_created = models.DateField(default=date.today)
    city_created = models.CharField(max_length=100)
    seller = models.ForeignKey(Contractor, on_delete=models.CASCADE, null=True, related_name='seller')
    buyer = models.ForeignKey(Contractor, on_delete=models.PROTECT, null=True, related_name='buyer')
    total_nett = models.FloatField(default=0.00)
    total_tax = models.FloatField(default=0.00)
    total_gross = models.FloatField(default=0.00)
    bank_num_account = models.CharField(max_length=100)
    date_supply = models.DateField(default=timezone.now)
    date_due = models.DateField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = models.Manager()

    @staticmethod
    def get_absolute_url():
        return reverse('invoice-list')
