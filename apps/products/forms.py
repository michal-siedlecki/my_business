from django.forms import ModelForm, NumberInput
from rest_framework import serializers

from .models import Product

PRODUCT_FIELDS = ['product_id', 'name', 'price_nett', 'tax_rate', 'price_gross']
PRODUCT_INVOICE_FIELDS = [*PRODUCT_FIELDS, 'quantity', 'prod_total_nett', 'prod_total_tax', 'prod_total_gross']


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = PRODUCT_FIELDS
        widgets = {
            'price_nett': NumberInput(attrs={'oninput': 'updateGross();'}),
            'tax_rate': NumberInput(attrs={'oninput': 'updateGross();'}),
            'price_gross': NumberInput(attrs={'oninput': 'updateNett();'})
        }


class ProductInvoiceForm(ModelForm):
    class Meta:
        model = Product
        fields = PRODUCT_INVOICE_FIELDS
        widgets = {
            'price_nett': NumberInput(attrs={'oninput': 'updateGrosses();'}),
            'tax_rate': NumberInput(attrs={'oninput': 'updateGrosses();'}),
            'price_gross': NumberInput(attrs={'oninput': 'updateNetts();'}),
            'quantity': NumberInput(attrs={'oninput': 'updateGrosses();', 'value': 0}),
            'prod_total_nett': NumberInput(attrs={'value': 0, 'readonly': True}),
            'prod_total_tax': NumberInput(attrs={'value': 0, 'readonly': True}),
            'prod_total_gross': NumberInput(attrs={'value': 0, 'readonly': True})
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = PRODUCT_FIELDS


class ProductInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = PRODUCT_INVOICE_FIELDS

    def get_list(self):
        data = self.initial_data
        dicts = []
        product_num = len(data.getlist(PRODUCT_INVOICE_FIELDS[0]))
        for num in range(product_num):
            d = dict.fromkeys(PRODUCT_INVOICE_FIELDS)
            for key in data.keys():
                if key in PRODUCT_INVOICE_FIELDS:
                    d[key] = data.getlist(key)[num-1]
            dicts.append(d)
        return dicts







