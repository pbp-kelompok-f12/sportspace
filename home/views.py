# home/views.py
import requests
import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core import serializers
from .models import LapanganPadel
from .forms import LapanganPadelForm

def get_google_maps_data(query="lapangan padel di jakarta"):
    api_key = settings.GOOGLE_MAPS_API_KEY
    if not api_key:
        print("Google Maps API key not configured")
        return []
        
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {'query': query, 'key': api_key, 'type': 'sports_complex'}
    venues = []
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if data.get('status') != 'OK':
            print(f"Google Maps API error: {data.get('error_message', 'Unknown error')}")
            return []
            
        results = data.get('results', [])
        for place in results:
            photo_url = None
            if place.get('photos'):
                photo_reference = place['photos'][0]['photo_reference']
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={api_key}"
            venue_data = {
                'place_id': place['place_id'], 
                'nama': place['name'],
                'alamat': place.get('formatted_address', 'Alamat tidak tersedia'),
                'rating': place.get('rating', 0),
                'total_review': place.get('user_ratings_total', 0),
                'thumbnail_url': photo_url,
            }
            venues.append(venue_data)
    except requests.exceptions.RequestException as e:
        print(f"Error saat request ke Google Maps API: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return venues


def landing(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, "landing.html")

@login_required(login_url='/accounts/login/')
def home_view(request):
    
    return render(request, 'home/index.html')

@login_required(login_url='/accounts/login/')
def get_lapangan_modal(request, id=None):
    if id:
        lapangan = get_object_or_404(LapanganPadel, pk=id)
        form = LapanganPadelForm(instance=lapangan)
        title = 'Edit Lapangan'
        submit_text = 'Update'
    else:
        lapangan = None
        form = LapanganPadelForm()
        title = 'Add New Lapangan'
        submit_text = 'Add Lapangan'
    context = {'form': form, 'title': title, 'submit_text': submit_text, 'lapangan': lapangan}
    return render(request, 'home/modal.html', context)


@login_required(login_url='/accounts/login/')
def get_lapangan_json(request):
    lapangan_objects = LapanganPadel.objects.all()
    data = []
    for lapangan in lapangan_objects:
        data.append({
            "pk": lapangan.pk,
            "model": "home.lapanganpadel", # Meniru format serializer asli
            "fields": {
                "nama": lapangan.nama,
                "alamat": lapangan.alamat,
                "rating": lapangan.rating,
                "total_review": lapangan.total_review,
                "thumbnail_url": lapangan.thumbnail_url,
                "is_featured": lapangan.is_featured,
                
                # Secara eksplisit tambahkan ID user yang membuat data ini.
                # Jika `added_by` kosong (untuk data lama), kirim `None`.
                "added_by": lapangan.added_by.id if lapangan.added_by else None
            }
        })
    return JsonResponse(data, safe=False)

@login_required(login_url='/accounts/login/')
def get_lapangan_by_id(request, id):
    try:
        lapangan = LapanganPadel.objects.get(pk=id)
        data = {
            'id': lapangan.id,
            'place_id': lapangan.place_id,
            'nama': lapangan.nama,
            'alamat': lapangan.alamat,
            'rating': lapangan.rating,
            'total_review': lapangan.total_review,
            'thumbnail_url': lapangan.thumbnail_url,
            'notes': lapangan.notes,
            'is_featured': lapangan.is_featured,
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
        
        # 'place_id' tidak lagi diperlukan dari user
        required_fields = ['nama', 'alamat']
        if not all(field in data and data[field] for field in required_fields):
            return JsonResponse({'status': 'error', 'message': 'Nama dan Alamat wajib diisi.'}, status=400)
        
        # Generate place_id unik secara acak
        new_place_id = f"internal_{uuid.uuid4().hex}"
        # Pastikan ID yang digenerate belum pernah ada (sangat kecil kemungkinannya, tapi ini best practice)
        while LapanganPadel.objects.filter(place_id=new_place_id).exists():
            new_place_id = f"internal_{uuid.uuid4().hex}"

        lapangan = LapanganPadel.objects.create(
            place_id=new_place_id, # <-- Gunakan ID yang baru dibuat
            nama=data['nama'],
            alamat=data['alamat'],
            rating=data.get('rating') or None,
            total_review=data.get('total_review') or None,
            thumbnail_url=data.get('thumbnail_url', ''),
            notes=data.get('notes', ''),
            is_featured=data.get('is_featured', False),
            added_by=request.user
        )
        
        return JsonResponse({'status': 'success', 'message': 'Lapangan berhasil ditambahkan!'}, status=201)
        
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
        
        # Update fields from data
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
        # Check if API key is configured
        if not settings.GOOGLE_MAPS_API_KEY:
            return JsonResponse({
                'status': 'error', 
                'message': 'Google Maps API key not configured. Please contact administrator.'
            }, status=500)
        
        lapangan_from_api = get_google_maps_data("lapangan padel jabodetabek")
        
        if not lapangan_from_api:
            return JsonResponse({
                'status': 'error', 
                'message': 'No data received from Google Maps API. Please check API key and try again.'
            }, status=500)
        
        updated_count = 0
        created_count = 0
        
        for data in lapangan_from_api:
            try:
                obj, created = LapanganPadel.objects.update_or_create(
                    place_id=data['place_id'],
                    defaults={
                        'nama': data['nama'],
                        'alamat': data['alamat'],
                        'rating': data['rating'],
                        'total_review': data['total_review'],
                        'thumbnail_url': data['thumbnail_url'],
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                print(f"Error processing venue {data.get('nama', 'Unknown')}: {e}")
                continue
        
        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} new venues added, {updated_count} venues updated.',
        })
        
    except Exception as e:
        print(f"Error in refresh_from_api: {e}")
        return JsonResponse({
            'status': 'error', 
            'message': f'Failed to refresh data: {str(e)}'
        }, status=500)