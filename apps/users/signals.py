from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, Address


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        address = Address.objects.create()
        Profile.objects.create(user=instance, address=address)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.address.save()
    instance.profile.save()
