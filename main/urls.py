from django.urls import path
from main.views import landing, show_main, create_field, show_field, show_xml, show_json, show_xml_by_id,show_json_by_id
from main.views import edit_field, delete_field

app_name = 'main'

urlpatterns = [
    path('', landing, name='landing'),
    path('home/', show_main, name='home'),
    path('create-field/', create_field, name='create_field'),
    path('field/<str:id>/', show_field, name='show_field'),
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<str:field_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<str:field_id>/', show_json_by_id, name='show_json_by_id'),
    path('field/<uuid:id>/edit/', edit_field, name='edit_field'),
    path('field/<uuid:id>/delete', delete_field, name='delete_news'),
]
