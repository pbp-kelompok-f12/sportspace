# main/urls.py
from django.urls import path
from main.views import (
    show_main, 
    create_venue, 
    show_venue,
    delete_venue, 
    edit_venue,
    show_xml, 
    show_json, 
    show_xml_by_id,
    show_json_by_id
)

app_name = 'main'

urlpatterns = [
    # Main dashboard
    path('', show_main, name='show_main'),
    
    # Venue CRUD
    path('create-venue/', create_venue, name='create_venue'),
    path('venue/<uuid:id>/', show_venue, name='show_venue'),
    path('venue/<uuid:id>/edit/', edit_venue, name='edit_venue'),
    path('venue/<uuid:id>/delete/', delete_venue, name='delete_venue'),
    
    # JSON/XML endpoints
    path('xml/', show_xml, name='show_xml'),
    path('json/', show_json, name='show_json'),
    path('xml/<uuid:venue_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/<uuid:venue_id>/', show_json_by_id, name='show_json_by_id'),
]