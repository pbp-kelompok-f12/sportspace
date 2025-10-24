# home/urls.py
from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home_view, name='home'),
    
    # URL BARU: Untuk memuat konten modal secara dinamis
    path('lapangan/modal/add/', views.get_lapangan_modal, name='get_lapangan_modal_add'),
    path('lapangan/modal/edit/<int:id>/', views.get_lapangan_modal, name='get_lapangan_modal_edit'),
    
    # JSON endpoints (tetap sama)
    path('api/lapangan/', views.get_lapangan_json, name='get_lapangan_json'),
    path('api/lapangan/<int:id>/', views.get_lapangan_by_id, name='get_lapangan_by_id'),
    
    # AJAX endpoints (tetap sama)
    path('api/lapangan/create/', views.create_lapangan_ajax, name='create_lapangan_ajax'),
    path('api/lapangan/<int:id>/update/', views.update_lapangan_ajax, name='update_lapangan_ajax'),
    path('api/lapangan/<int:id>/delete/', views.delete_lapangan_ajax, name='delete_lapangan_ajax'),
    path('api/lapangan/refresh/', views.refresh_from_api, name='refresh_from_api'),
]