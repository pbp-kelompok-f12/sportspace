from django.forms import ModelForm
from .models import Field, Booking

class FieldForm(ModelForm):
    class Meta:
        model = Field
        fields = ["name", "sport_type", "location", "price_per_hour", "is_available"]

class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = ["field", "customer_name", "start_time", "end_time", "total_price"]