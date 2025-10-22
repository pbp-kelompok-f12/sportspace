from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile/json/', views.profile_json, name='profile_json'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/venue-owner/', views.venue_dashboard, name='venue_dashboard'),
]
