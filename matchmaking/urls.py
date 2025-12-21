from django.urls import path
from . import views

app_name = 'matchmaking'

urlpatterns = [
    # WEB (dummy)
    path('', views.matchmaking_home, name='home'),
    path('1vs1/', views.one_vs_one, name='one_vs_one'),
    path('2vs2/', views.two_vs_two, name='two_vs_two'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),

    # JSON API (Flutter)
    path('json/', views.list_match_json, name='list_match_json'),
    path('json/<int:match_id>/', views.detail_match_json, name='detail_match_json'),

    path('create-1v1/', views.create_1v1_flutter, name='create_1v1_flutter'),
    path('create-2v2/', views.create_2v2_flutter, name='create_2v2_flutter'),
    path('join/<int:match_id>/', views.join_match_flutter, name='join_match_flutter'),
    path('delete/<int:match_id>/', views.delete_match_flutter, name='delete_match_flutter'),
]
