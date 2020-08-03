from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import Profile, Address


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        address = Address.objects.create()
        address.save()
        Profile.objects.create(user=instance, address=address)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


