import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Vendor(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="venues")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    contact = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
    
class Venue(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255)
    
    description = models.TextField(blank=True)
    facilities = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    price_per_hour = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    # Rating berdasarkan rata rata dari review yang ada
    @property
    def average_rating(self):
        agg = self.reviews.aggregate(avg=Avg('rating'))
        return round(agg['avg'] or 0, 1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_sport_type_display()}"


