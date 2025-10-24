from django.urls import path
from . import views

app_name = 'matchmaking'

urlpatterns = [
    path('', views.matchmaking_home, name='home'),
    path('1vs1/', views.one_vs_one, name='one_vs_one'),
    path('2vs2/', views.two_vs_two, name='two_vs_two'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('match/<int:match_id>/join/', views.join_match, name='join_match'),
    path('match/<int:match_id>/delete/', views.delete_match, name='delete_match'),
]
