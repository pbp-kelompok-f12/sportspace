from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('venue/<uuid:venue_id>/', views.venue_booking, name='venue_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('api/create-booking/', views.create_booking, name='create_booking'),
    path('api/update-booking/<uuid:booking_id>/', views.update_booking, name='update_booking'),
    path('api/delete-booking/<uuid:booking_id>/', views.delete_booking, name='delete_booking'),
]
