from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile, SellerProfile


@receiver(post_save, sender=User)
def ensure_profiles(sender, instance, **kwargs):
    # Every user gets Profile
    Profile.objects.get_or_create(user=instance)

    # Seller gets SellerProfile
    if instance.role == "seller":
        SellerProfile.objects.get_or_create(
            user=instance,
            defaults={
                "business_name": instance.username,
                "business_email": instance.email or "",
                "region": "dar_es_salaam",
            }
        )
