from django.urls import path
from main.views import show_main, create_field, show_field, show_xml, show_json, show_xml_by_id,show_json_by_id
from main.views import register, login_user, logout_user, edit_field, delete_field

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-field/', create_field, name='create_field'),
    path('field/<str:id>/', show_field, name='show_field'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:field_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:field_id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('field/<uuid:id>/edit/', edit_field, name='edit_field'),
    path('field/<uuid:id>/delete', delete_field, name='delete_news'),
]
