from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    # path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile/json/', views.profile_json, name='profile_json'),
]
