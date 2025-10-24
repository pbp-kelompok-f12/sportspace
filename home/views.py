# home/views.py
import requests
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core import serializers
from .models import LapanganPadel
from review.models import Review

def get_google_maps_data(query="lapangan padel di jakarta"):
    """Fungsi untuk mengambil data dari Google Places API."""
    
    api_key = settings.GOOGLE_MAPS_API_KEY
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        'query': query,
        'key': api_key,
        'type': 'sports_complex'
    }
    
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
                'place_id': place['place_id'],
                'nama': place['name'],
                'alamat': place.get('formatted_address', 'Alamat tidak tersedia'),
                'rating': place.get('rating', 0),
                'total_review': place.get('user_ratings_total', 0),
                'thumbnail_url': photo_url,
            }
            venues.append(venue_data)

    except requests.exceptions.RequestException as e:
        print(f"Error saat request ke API: {e}")
        return []

    return venues


def landing(request):
    """Landing page untuk user yang belum login"""
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, "landing.html")


@login_required(login_url='/accounts/login/')
def home_view(request):
    """Home page setelah login - menampilkan lapangan padel"""
    # Ambil data dari Google Maps API
    lapangan_from_api = get_google_maps_data("lapangan padel jabodetabek")

    # Simpan atau update data ke database
    for data in lapangan_from_api:
        LapanganPadel.objects.update_or_create(
            place_id=data['place_id'],
            defaults={
                'nama': data['nama'],
                'alamat': data['alamat'],
                'rating': data['rating'],
                'total_review': data['total_review'],
                'thumbnail_url': data['thumbnail_url'],
            }
        )
    
    # Ambil semua data dari database untuk ditampilkan
    places = LapanganPadel.objects.all()

    context = {
        'username': request.user.username,
        'places': places,
    }
    
    return render(request, 'index.html', context)


# ==================== AJAX ENDPOINTS ====================

@login_required(login_url='/accounts/login/')
def get_lapangan_json(request):
    """Get all lapangan in JSON format"""
    lapangan = LapanganPadel.objects.all()
    return HttpResponse(serializers.serialize('json', lapangan), content_type="application/json")


@login_required(login_url='/accounts/login/')
def get_lapangan_by_id(request, id):
    """Get lapangan by ID in JSON format"""
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
    """Create new lapangan via AJAX"""
    try:
        data = json.loads(request.body)
        
        # Validasi data required
        required_fields = ['place_id', 'nama', 'alamat']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'status': 'error',
                    'message': f'{field} is required'
                }, status=400)
        
        # Cek apakah place_id sudah ada
        if LapanganPadel.objects.filter(place_id=data['place_id']).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Lapangan dengan place_id ini sudah ada'
            }, status=400)
        
        # Create lapangan
        lapangan = LapanganPadel.objects.create(
            place_id=data['place_id'],
            nama=data['nama'],
            alamat=data['alamat'],
            rating=data.get('rating'),
            total_review=data.get('total_review'),
            thumbnail_url=data.get('thumbnail_url', ''),
            notes=data.get('notes', ''),
            is_featured=data.get('is_featured', False)
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Lapangan berhasil ditambahkan',
            'data': {
                'id': lapangan.id,
                'nama': lapangan.nama,
                'alamat': lapangan.alamat,
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required(login_url='/accounts/login/')
def update_lapangan_ajax(request, id):
    """Update lapangan via AJAX"""
    try:
        lapangan = LapanganPadel.objects.get(pk=id)
        data = json.loads(request.body)
        
        # Update fields
        if 'nama' in data:
            lapangan.nama = data['nama']
        if 'alamat' in data:
            lapangan.alamat = data['alamat']
        if 'rating' in data:
            lapangan.rating = data['rating']
        if 'total_review' in data:
            lapangan.total_review = data['total_review']
        if 'thumbnail_url' in data:
            lapangan.thumbnail_url = data['thumbnail_url']
        if 'notes' in data:
            lapangan.notes = data['notes']
        if 'is_featured' in data:
            lapangan.is_featured = data['is_featured']
        
        lapangan.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Lapangan berhasil diupdate',
            'data': {
                'id': lapangan.id,
                'nama': lapangan.nama,
                'alamat': lapangan.alamat,
            }
        })
        
    except LapanganPadel.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Lapangan not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required(login_url='/accounts/login/')
def delete_lapangan_ajax(request, id):
    """Delete lapangan via AJAX"""
    try:
        lapangan = LapanganPadel.objects.get(pk=id)
        lapangan.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Lapangan berhasil dihapus'
        })
        
    except LapanganPadel.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Lapangan not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required(login_url='/accounts/login/')
def refresh_from_api(request):
    """Refresh data dari Google Maps API"""
    try:
        lapangan_from_api = get_google_maps_data("lapangan padel jabodetabek")
        
        updated_count = 0
        created_count = 0
        
        for data in lapangan_from_api:
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
        
        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} lapangan baru ditambahkan, {updated_count} lapangan diupdate',
            'created': created_count,
            'updated': updated_count
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def detail_lapangan(request, id):
    lapangan = get_object_or_404(LapanganPadel, pk=id)
    reviews = lapangan.reviews.all()[:4]  # ambil 4 review terbaru
    context = {
        'lapangan': lapangan,
        'reviews': reviews,
    }
    return render(request, 'home/detail_lapangan_new.html', context)

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