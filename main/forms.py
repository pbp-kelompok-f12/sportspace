from django.forms import ModelForm
from .models import Venue, Booking, Venue

class VenueForm(ModelForm):
    class Meta:
        model = Venue
        fields = ["name", "location", "price_per_hour", "is_available"]

class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = ["venue", "customer_name", "start_time", "end_time", "total_price"]