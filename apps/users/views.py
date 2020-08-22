from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserRegisterForm, \
    UserUpdateForm, \
    ProfileUpdateForm, \
    AddressForm
from .models import Profile
from mybusiness import serializers, services


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('invoice-list')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        profile = Profile.objects.get(user=user)
        address = profile.address
        serializer_profile = serializers.ProfileSerializer(data=request.POST)
        serializer_address = serializers.AddressSerializer(data=request.POST)
        serializer_address.is_valid(raise_exception=True)
        serializer_profile.is_valid(raise_exception=True)
        services.update_profile(
            profile_pk=profile.pk,
            data=serializer_profile.validated_data,
            address_pk=address.pk,
            address_data=serializer_address.validated_data
        )
        messages.success(request, 'Profile updated')
        return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        address_form = AddressForm(instance=request.user.profile.address)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'address_form': address_form
    }
    return render(request, 'users/profile.html', context)
