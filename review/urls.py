from django.urls import path
from . import views

app_name = "review"

urlpatterns = [
    path("<uuid:field_id>/add/", views.add_review, name="add_review"),
    path("<uuid:field_id>/", views.show_reviews, name="show_reviews"),
]
