from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/json/', views.profile_json, name='profile_json'),

    path('login-flutter/', views.login_flutter, name='login_flutter'), 
    path('register-flutter/', views.register_flutter, name='register_flutter'),

    path("friends/send/", views.send_friend_request, name="send_friend_request"),
    path("handle-friend-request/", views.handle_friend_request, name="handle_friend_request"),
    path("friends/", views.friends_json, name="friends_json"),
    path("unfriend/", views.unfriend, name="unfriend"),
    path("friends/count/", views.get_friend_count, name="get_friend_count"),
    path("friend-requests/count/", views.get_request_count, name="get_request_count"),
    path("friends/suggestions/", views.get_friend_suggestions, name="get_friend_suggestions"),

    path("chat/<str:username>/", views.get_chat_history, name="get_chat_history"),
    path("chat/send/", views.send_chat_message, name="send_chat_message"),
]
