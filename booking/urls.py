from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('venue/<uuid:venue_id>/', views.venue_booking, name='venue_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('api/create-booking/', views.create_booking, name='create_booking'),
    path('api/update-booking/<uuid:booking_id>/', views.update_booking, name='update_booking'),
    path('api/delete-booking/<uuid:booking_id>/', views.delete_booking, name='delete_booking'),
    path('api/delete-booking-post/<uuid:booking_id>/', views.delete_booking_post, name='delete_booking_post'),
    path('api/sync-venue/', views.sync_venue, name='sync_venue'),
    path('api/venue-time-slots/<uuid:venue_id>/', views.api_venue_time_slots, name='api_venue_time_slots'),
    path('api/my-bookings-json/', views.api_my_bookings, name='api_my_bookings'),
]
