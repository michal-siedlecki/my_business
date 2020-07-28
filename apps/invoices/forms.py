from datetime import date, timezone
from rest_framework import serializers
from django import forms
from django.forms import ModelForm, NumberInput, DateInput

from apps.contractors.models import Contractor
from .models import Invoice


class InvoiceForm(ModelForm):
    total_nett = forms.NumberInput(attrs={'label': ''})

    class Meta:
        model = Invoice
        fields = [
            'invoice_id',
            'date_created',
            'date_supply',
            'city_created',
            'buyer',
            'total_nett',
            'total_tax',
            'total_gross',
            'date_due'
        ]
        widgets = {
            'total_nett': NumberInput(attrs={'value': 0, 'readonly': True}),
            'total_tax': NumberInput(attrs={'value': 0, 'readonly': True}),
            'total_gross': NumberInput(attrs={'value': 0, 'readonly': True}),
            'date_created': DateInput(attrs={'id': 'datepicker1'}),
            'date_supply': DateInput(attrs={'id': 'datepicker2'}),
            'date_due': DateInput(attrs={'id': 'datepicker3'})
        }

    def __init__(self, user, buyer=None, *args, **kwargs):
        super(InvoiceForm, self).__init__(*args, **kwargs)
        self.fields['buyer'].queryset = Contractor.objects.filter(author=user, on_invoice=False)
        self.fields['city_created'].initial = user.profile.address.city
        self.fields['invoice_id'].initial = "FV_01"
        if buyer:
            contractor_1 = Contractor.objects.filter(pk=self.instance.buyer.pk)
            contractor_2 = Contractor.objects.filter(author=user, on_invoice=False)
            self.fields['buyer'].queryset = contractor_1 | contractor_2
            
            
    def populate_form_fields(self, user):
        author = user
        seller_contractor = user.profile.make_contractor(author=author)
        seller_contractor.save()
        self.instance.seller = seller_contractor
        buyer_contractor = self.instance.buyer.copy(author=author)
        buyer_contractor.save()
        self.instance.buyer = buyer_contractor
        self.instance.author = author
        self.instance.bank_num_account = author.profile.bank_account_num
        return self
            
            
class InvoiceSerializer(serializers.Serializer):
    invoice_id = serializers.CharField(max_length=100)
    date_created = serializers.DateField(default=date.today)
    city_created = serializers.CharField(max_length=100)
    total_nett = serializers.FloatField(default=0.00)
    total_tax = serializers.FloatField(default=0.00)
    total_gross = serializers.FloatField(default=0.00)
    date_supply = serializers.DateField(default=date.today)
    date_due = serializers.DateField(default=date.today)

