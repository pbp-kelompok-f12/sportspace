from django.urls import path
from . import views

app_name = "review"
urlpatterns = [
    # Path web url
    path("lapangan/<int:id>/", views.all_reviews, name="all_reviews"),
    path('my/', views.my_reviews, name='my_reviews'),
    path('edit/<int:pk>/', views.edit_review, name='edit_review'),
    path('delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('all/<int:id>/', views.all_reviews, name='all_reviews'),
    
    # Path API url
    path('api/my-reviews/', views.api_my_reviews, name='api_my_reviews'),
    path('api/venue/<int:lapangan_id>/', views.api_venue_reviews, name='api_venue_reviews'),
    path('api/create/', views.api_create_review, name='api_create_review'),
    path('api/update/<int:pk>/', views.api_update_review, name='api_update_review'),
    path('api/delete/<int:pk>/', views.api_delete_review, name='api_delete_review'),
    path('proxy-image/', views.proxy_image, name='proxy_image'),
    path('api/unreviewed-venues/', views.api_get_unreviewed_venues, name='api_get_unreviewed_venues'),
]
