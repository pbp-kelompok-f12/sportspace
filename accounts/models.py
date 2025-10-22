from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('venue_owner', 'Venue Owner')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    photo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"