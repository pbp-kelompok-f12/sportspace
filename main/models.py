import uuid
from django.db import models
from django.contrib.auth.models import User

class Vendor(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="venues")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    contact = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
    
class Field(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)

    SPORT_CHOICES = [
        ('futsal', 'Futsal'),
        ('badminton', 'Badminton'),
        ('basket', 'Basketball'),
        ('tennis', 'Tennis'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    sport_type = models.CharField(max_length=20, choices=SPORT_CHOICES)
    location = models.CharField(max_length=255)
    price_per_hour = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_sport_type_display()}"


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_price = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.customer_name} - {self.field.name}"

    @property
    def duration_hours(self):
        """Hitung durasi booking dalam jam."""
        diff = self.end_time - self.start_time
        return diff.total_seconds() / 3600
