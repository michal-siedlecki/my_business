from django.forms import ModelForm, NumberInput

from .models import Product


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_id',
            'name',
            'price_nett',
            'tax_rate',
            'price_gross'
        ]
        widgets = {
            'price_nett': NumberInput(attrs={'oninput': 'updateGross();'}),
            'tax_rate': NumberInput(attrs={'oninput': 'updateGross();'}),
            'price_gross': NumberInput(attrs={'oninput': 'updateNett();'})
        }


class ProductInvoiceForm(ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_id',
            'name',
            'price_nett',
            'tax_rate',
            'price_gross',
            'quantity',
            'prod_total_nett',
            'prod_total_tax',
            'prod_total_gross'
        ]
        widgets = {
            'price_nett': NumberInput(attrs={'oninput': 'updateGrosses();'}),
            'tax_rate': NumberInput(attrs={'oninput': 'updateGrosses();'}),
            'price_gross': NumberInput(attrs={'oninput': 'updateNetts();'}),
            'quantity': NumberInput(attrs={'oninput': 'updateGrosses();', 'value': 0}),
            'prod_total_nett': NumberInput(attrs={'value': 0, 'readonly': True}),
            'prod_total_tax': NumberInput(attrs={'value': 0, 'readonly': True}),
            'prod_total_gross': NumberInput(attrs={'value': 0, 'readonly': True})
        }

    def __init__(self, *args, **kwargs):
        super(ProductInvoiceForm, self).__init__(*args, **kwargs)
        self.fields['product_id'].label = "ID"

    def populate_fields(self, invoice):
        self.instance.author = invoice.author
        self.instance.document = invoice
        return self
