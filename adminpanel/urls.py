from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Dashboard utama
    path('', views.dashboard, name='dashboard'),

    # Lapangan
    path('lapangan/', views.dashboard_lapangan_ajax, name='dashboard_lapangan'),
    path('lapangan/data/', views.get_lapangan_json, name='get_lapangan_json'),
    path('lapangan/add/', views.create_lapangan_ajax, name='create_lapangan_ajax'),
    path('lapangan/update/<int:id>/', views.update_lapangan_ajax, name='update_lapangan_ajax'),
    path('lapangan/delete/<int:id>/', views.delete_lapangan_ajax, name='delete_lapangan_ajax'),

    # Pengguna
    path('users/', views.dashboard_user_admin, name='dashboard_user_admin'),
    path('users/data/', views.get_users_json, name='get_users_json'),
    path('users/add/', views.add_user_ajax, name='add_user_ajax'),
    path('users/update/<int:id>/', views.update_user_ajax, name='update_user_ajax'),
    path('users/delete/<int:id>/', views.delete_user_ajax, name='delete_user_ajax'),
    
    # Booking
    path('bookings/', views.dashboard_booking_ajax, name='dashboard_booking'),
    path('bookings/data/', views.get_booking_json, name='get_booking_json'),
    path('bookings/delete/<uuid:id>/', views.delete_booking_ajax, name='delete_booking_ajax'),
]
