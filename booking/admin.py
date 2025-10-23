from django.contrib import admin
from .models import Venue, Booking

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at']
    search_fields = ['name', 'location']
    list_filter = ['created_at']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['venue', 'user', 'booking_date', 'start_time', 'customer_name']
    search_fields = ['venue__name', 'user__username', 'customer_name']
    list_filter = ['booking_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']