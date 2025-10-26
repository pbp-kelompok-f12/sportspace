from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

    bio = models.TextField(blank=True, default="", help_text="Deskripsi singkat tentang diri pengguna")
    total_booking = models.PositiveIntegerField(default=0, help_text="Jumlah booking yang pernah dilakukan")
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text="Rata-rata rating pengguna")
    joined_date = models.DateField(default=timezone.now, editable=False, help_text="Tanggal pengguna bergabung")

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
     # ===== Dinamis dari model Booking dan Review =====
    @property
    def total_booking(self):
        from booking.models import Booking 
        return Booking.objects.filter(user=self.user).count()

    @property
    def avg_rating(self):
        from review.models import Review
        ratings = Review.objects.filter(user=self.user).values_list('rating', flat=True)
        if ratings:
            return round(sum(ratings) / len(ratings), 1)
        return 0
    
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
