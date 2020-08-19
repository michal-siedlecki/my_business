from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from mybusiness import services, serializers
from apps.users.forms import AddressForm
from .forms import ContractorForm
from .models import Contractor


class ContractorListView(LoginRequiredMixin, ListView):
    model = Contractor
    template_name = 'contractors/contractors.html'
    context_object_name = 'contractors'

    def get_queryset(self):
        return ContractorListView.model.objects.filter(author=self.request.user, on_invoice=False)


class ContractorCreateView(LoginRequiredMixin, CreateView):
    template_name = 'contractors/contractor_form.html'
    success_url = 'contractors'
    contractor_form = ContractorForm
    address_form = AddressForm

    def get_context_data(self, **kwargs):
        context = {
            'contractor_form': self.contractor_form,
            'address_form': self.address_form,
            'submit_button': 'Create'
        }
        return context

    def contractor_form_valid(self, form, address):
        form.instance.author = self.request.user
        form.instance.address = address
        return form

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer_contractor = serializers.ContractorSerializer(data=request.POST)
        serializer_address = serializers.AddressSerializer(data=request.POST)
        serializer_address.is_valid(raise_exception=True)
        serializer_contractor.is_valid(raise_exception=True)
        services.create_contractor(
            data=serializer_contractor.validated_data,
            address=serializer_address.validated_data,
            user=user
        )
        messages.success(request, f'Contractor created')
        return redirect('contractor-list')


class ContractorUpdateView(ContractorCreateView, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Contractor

    def get_context_data(self):
        contractor = self.get_object()
        contractor_form = ContractorForm(instance=contractor)
        address_form = AddressForm(instance=contractor.address)

        context = {
            'contractor_form': contractor_form,
            'address_form': address_form,
            'submit_button': 'Update'
        }
        return context

    def post(self, request, *args, **kwargs):
        contractor = self.get_object()
        serializer_contractor = serializers.ContractorSerializer(data=request.POST)
        serializer_address = serializers.AddressSerializer(data=request.POST)
        serializer_address.is_valid(raise_exception=True)
        serializer_contractor.is_valid(raise_exception=True)
        services.update_contractor(
            contractor_pk=contractor.pk,
            data=serializer_contractor.validated_data,
            address_pk=contractor.address.pk,
            address_data=serializer_address.validated_data
        )
        messages.success(request, f'Contractor updated')
        return redirect('contractor-list')

    def test_func(self):
        contractor = self.get_object()
        return self.request.user == contractor.author


class ContractorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Contractor
    success_url = '/contractors'

    def test_func(self):
        contractor = self.get_object()
        return self.request.user == contractor.author
