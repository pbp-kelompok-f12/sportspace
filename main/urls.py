from django.urls import path
from main.views import edit_venue, show_main, create_venue, show_list_venue, show_xml, show_json, show_xml_by_id,show_json_by_id
from main.views import register, login_user, logout_user, edit_venue, delete_venue

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('create-venue/', create_venue, name='create_venue'),
    path('venue/<str:id>/', show_list_venue, name='show_list_venue'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:field_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:field_id>/', show_json_by_id, name='show_json_by_id'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('field/<uuid:id>/edit/', edit_venue, name='edit_venue'),
    path('field/<uuid:id>/delete', delete_venue, name='delete_venue'),
]
