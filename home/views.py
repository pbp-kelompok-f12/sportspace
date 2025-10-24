# home/views.py
import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core import serializers
from .models import LapanganPadel
from .forms import LapanganPadelForm
from review.models import Review

def get_google_maps_data(query="lapangan padel di jakarta"):
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {'query': query, 'key': api_key, 'type': 'sports_complex'}
    venues = []
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get('results', [])
        for place in results:
            photo_url = None
            if place.get('photos'):
                photo_reference = place['photos'][0]['photo_reference']
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"
            venue_data = {
                'place_id': place['place_id'], 'nama': place['name'],
                'alamat': place.get('formatted_address', 'Alamat tidak tersedia'),
                'rating': place.get('rating', 0),
                'total_review': place.get('user_ratings_total', 0),
                'thumbnail_url': photo_url,
            }
            venues.append(venue_data)
    except requests.exceptions.RequestException as e:
        print(f"Error saat request ke API: {e}")
    return venues

def landing(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, "landing.html")

@login_required(login_url='/accounts/login/')
def home_view(request):
    places = LapanganPadel.objects.all()
    context = {
        'username': request.user.username,
        'places': places,
    }
    return render(request, 'index.html', context)

# ... (AJAX endpoints seperti get_lapangan_json, create_lapangan_ajax, dll. tetap sama) ...
@login_required(login_url='/accounts/login/')
def get_lapangan_json(request):
    lapangan = LapanganPadel.objects.all()
    data = serializers.serialize('json', lapangan)
    return HttpResponse(data, content_type="application/json")

@login_required(login_url='/accounts/login/')
def get_lapangan_by_id(request, id):
    try:
        lapangan = LapanganPadel.objects.get(pk=id)
        data = {
            'id': lapangan.id, 'place_id': lapangan.place_id, 'nama': lapangan.nama,
            'alamat': lapangan.alamat, 'rating': lapangan.rating, 'total_review': lapangan.total_review,
            'thumbnail_url': lapangan.thumbnail_url, 'notes': lapangan.notes, 'is_featured': lapangan.is_featured,
        }
        return JsonResponse(data)
    except LapanganPadel.DoesNotExist:
        return JsonResponse({'error': 'Lapangan not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='/accounts/login/')
def create_lapangan_ajax(request):
    try:
        data = json.loads(request.body)
        required_fields = ['place_id', 'nama', 'alamat']
        if not all(field in data and data[field] for field in required_fields):
            return JsonResponse({'status': 'error', 'message': 'Place ID, Nama, and Alamat are required.'}, status=400)
        if LapanganPadel.objects.filter(place_id=data['place_id']).exists():
            return JsonResponse({'status': 'error', 'message': 'Lapangan with this Place ID already exists.'}, status=400)
        
        lapangan = LapanganPadel.objects.create(
            place_id=data['place_id'], nama=data['nama'], alamat=data['alamat'],
            rating=data.get('rating'), total_review=data.get('total_review'),
            thumbnail_url=data.get('thumbnail_url', ''), notes=data.get('notes', ''),
            is_featured=data.get('is_featured', False), added_by=request.user
        )
        return JsonResponse({'status': 'success', 'message': 'Lapangan added successfully!'}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='/accounts/login/')
def update_lapangan_ajax(request, id):
    try:
        lapangan = get_object_or_404(LapanganPadel, pk=id)
        if lapangan.added_by != request.user and not request.user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this.'}, status=403)
        data = json.loads(request.body)
        for field, value in data.items():
            if hasattr(lapangan, field):
                setattr(lapangan, field, value)
        lapangan.save()
        return JsonResponse({'status': 'success', 'message': 'Lapangan updated successfully!'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required(login_url='/accounts/login/')
def delete_lapangan_ajax(request, id):
    try:
        lapangan = get_object_or_404(LapanganPadel, pk=id)
        if lapangan.added_by != request.user and not request.user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'You do not have permission to delete this.'}, status=403)
        lapangan.delete()
        return JsonResponse({'status': 'success', 'message': 'Lapangan deleted successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required(login_url='/accounts/login/')
def refresh_from_api(request):
    try:
        lapangan_from_api = get_google_maps_data("lapangan padel jabodetabek")
        updated_count, created_count = 0, 0
        for data in lapangan_from_api:
            obj, created = LapanganPadel.objects.update_or_create(
                place_id=data['place_id'],
                defaults={
                    'nama': data['nama'], 'alamat': data['alamat'], 'rating': data['rating'],
                    'total_review': data['total_review'], 'thumbnail_url': data['thumbnail_url'],
                }
            )
            created_count += 1 if created else 0
            updated_count += 0 if created else 1
        return JsonResponse({'status': 'success', 'message': f'{created_count} new venues added, {updated_count} venues updated.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# Fungsi create_lapangan_page dihapus

@login_required(login_url='/accounts/login/')
def edit_lapangan_page(request, id):
    lapangan = get_object_or_404(LapanganPadel, pk=id)
    if lapangan.added_by != request.user and not request.user.is_superuser:
        return redirect('home:home')
    if request.method == 'POST':
        form = LapanganPadelForm(request.POST, instance=lapangan)
        if form.is_valid():
            form.save()
            return redirect('home:home')
    else:
        form = LapanganPadelForm(instance=lapangan)
    context = {
        'form': form, 'title': 'Edit Lapangan',
        'submit_text': 'Update Lapangan', 'lapangan': lapangan
    }
    return render(request, 'modal.html', context)


@login_required(login_url='/accounts/login/')
def get_lapangan_modal(request, id=None):
    """Mengembalikan konten HTML modal untuk tambah/edit."""
    if id:
        # Mode Edit
        lapangan = get_object_or_404(LapanganPadel, pk=id)
        form = LapanganPadelForm(instance=lapangan)
        title = 'Edit Lapangan'
        submit_text = 'Update'
    else:
        # Mode Tambah
        lapangan = None
        form = LapanganPadelForm()
        title = 'Add New Lapangan'
        submit_text = 'Add Lapangan'
        
    context = {
        'form': form,
        'title': title,
        'submit_text': submit_text,
        'lapangan': lapangan
    }
    return render(request, 'modal.html', context)
        

@login_required
def detail_lapangan(request, id):
    lapangan = get_object_or_404(LapanganPadel, pk=id)
    reviews = lapangan.reviews.all()[:4]  # ambil 4 review terbaru
    context = {
        'lapangan': lapangan,
        'reviews': reviews,
    }
    return render(request, 'home/detail_lapangan_new.html', context)
