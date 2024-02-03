from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from core.models import Profile  # Import inside the function to avoid circular import
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=User)
def save_top_up_transaction(sender, instance, created, **kwargs):
    # Check if the saving process is occurring in the Django admin site
    in_admin = kwargs.get('raw', False) or kwargs.get('using', False)

    if not in_admin:
        if created:
            from core.models import Profile, TopUpTransaction  # Import inside the function
            # Ensure the user has a profile before creating TopUpTransaction
            if hasattr(instance, 'profile'):
                # Create a new TopUpTransaction instance associated with the user
                TopUpTransaction.objects.create(user=instance)
            else:
                # Handle the case where the profile doesn't exist yet
                Profile.objects.create(user=instance)
                instance.profile.save()
                TopUpTransaction.objects.create(user=instance)