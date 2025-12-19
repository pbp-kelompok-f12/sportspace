from django.urls import path
from . import views

app_name = "review"
urlpatterns = [
    path("lapangan/<int:id>/", views.all_reviews, name="all_reviews"),
    path('my/', views.my_reviews, name='my_reviews'),
    path('edit/<int:pk>/', views.edit_review, name='edit_review'),
    path('delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('all/<int:id>/', views.all_reviews, name='all_reviews'),
]
