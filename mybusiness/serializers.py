from django.core import serializers as core_serializers
from rest_framework import serializers

from apps.contractors.models import Contractor
from apps.users.models import Address
from mybusiness import services


class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


def serialize_products_on_invoice(invoice):
    serializer = core_serializers.get_serializer("json")()
    invoice_products = serializer.serialize(
        services.get_invoice_products(invoice),
        ensure_ascii=False
    )
    return invoice_products


class InvoiceSerializer(serializers.Serializer):
    invoice_id = serializers.CharField(max_length=100)
    date_created = serializers.DateField()
    city_created = serializers.CharField(max_length=100)
    total_nett = serializers.FloatField(default=0.00)
    total_tax = serializers.FloatField(default=0.00)
    total_gross = serializers.FloatField(default=0.00)
    date_supply = serializers.DateField()
    date_due = serializers.DateField()
