from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.users.forms import AddressForm
from apps.users.models import Address
from .forms import ContractorForm
from .models import Contractor


class ContractorCreateView(LoginRequiredMixin, CreateView):
    template_name = 'contractors/contractor_form.html'
    success_url = 'contractors'
    contractor_form = ContractorForm
    address_form = AddressForm

    def get_context_data(self, **kwargs):
        context = {
            'contractor_form': self.contractor_form,
            'address_form': self.address_form
        }
        return context

    def contractor_form_valid(self, form, address):
        form.instance.author = self.request.user
        form.instance.address = address
        return form

    def post(self, request, *args, **kwargs):
        contractor_form = ContractorForm(data=request.POST, instance=Contractor())
        address_form = AddressForm(data=request.POST, instance=Address())
        if address_form.is_valid() and contractor_form.is_valid():
            address = address_form.save()
            contractor = self.contractor_form_valid(contractor_form, address).save(commit=False)
            contractor.save()
            messages.success(request, f'Contractor created')
            return redirect('contractor-list')
        return redirect('contractor-new')


class ContractorListView(LoginRequiredMixin, ListView):
    model = Contractor
    template_name = 'contractors/contractors.html'
    context_object_name = 'contractors'

    def get_queryset(self):
        return ContractorListView.model.objects.filter(author=self.request.user, on_invoice=False)


class ContractorUpdateView(ContractorCreateView, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Contractor

    def get_context_data(self):
        contractor = self.get_object()
        contractor_form = ContractorForm(instance=contractor)
        address_form = AddressForm(instance=contractor.address)

        context = {
            'contractor_form': contractor_form,
            'address_form': address_form,
        }
        return context

    def post(self, request, *args, **kwargs):
        contractor_form = ContractorForm(data=request.POST, instance=self.get_object())
        address_form = AddressForm(data=request.POST, instance=self.get_object().address)
        if address_form.is_valid() and contractor_form.is_valid():
            address_form.save()
            contractor_form.save()
            messages.success(request, f'Contractor updated')
            return redirect('contractor-list')
        return redirect('contractor-new')

    def test_func(self):
        contractor = self.get_object()
        return self.request.user == contractor.author


class ContractorDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Contractor
    success_url = '/contractors'

    def test_func(self):
        contractor = self.get_object()
        return self.request.user == contractor.author
