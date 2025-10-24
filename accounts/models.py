from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('venue_owner', 'Venue Owner'),
        ('admin', 'Admin')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Otomatis buat Profile saat user dibuat"""
    if created:

        Profile.objects.get_or_create(
            user=instance,
            defaults={'role': 'admin' if instance.is_superuser else 'customer'}
        )
    else:
        instance.profile.save()
