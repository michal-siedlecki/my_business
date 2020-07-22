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
