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
from booking.models import Venue
from .forms import LapanganPadelForm
from django.utils.html import strip_tags

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
    context = {
        'user_id': request.user.id,
        'is_superuser': request.user.is_superuser
    }
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


#@login_required(login_url='/accounts/login/')
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


@login_required(login_url='/accounts/login/')
def lapangan_to_venue(request, id):
    """
    Small helper API for mobile to map LapanganPadel pk to booking.Venue UUID.
    We use place_id and name/address to find or create a Venue via the
    existing sync logic.
    """
    try:
        lapangan = LapanganPadel.objects.get(pk=id)
    except LapanganPadel.DoesNotExist:
        return JsonResponse({'error': 'Lapangan not found'}, status=404)

    # Try to find existing Venue with same name & address
    venue, _ = Venue.objects.get_or_create(
        name=lapangan.nama,
        defaults={
            'location': lapangan.alamat,
            'address': lapangan.alamat,
            'image_url': lapangan.thumbnail_url,
            'description': f'Padel court located at {lapangan.alamat}',
        },
    )

    return JsonResponse({'venue_id': str(venue.id)})


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



def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)


@csrf_exempt
def create_lapangan_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            place_id = strip_tags(data.get("place_id", ""))
            nama = strip_tags(data.get("nama", ""))
            alamat = strip_tags(data.get("alamat", ""))
            rating = data.get("rating", None)
            total_review = data.get("total_review", None)
            thumbnail_url = data.get("thumbnail_url", "")
            notes = strip_tags(data.get("notes", ""))
            is_featured = data.get("is_featured", False)
            user = request.user

            if not place_id or not nama or not alamat:
                return JsonResponse({"status": "error", "message": "Place ID, Nama, dan Alamat tidak boleh kosong."}, status=400)

            lapangan = LapanganPadel(
                place_id=place_id,
                nama=nama,
                alamat=alamat,
                rating=rating,
                total_review=total_review,
                thumbnail_url=thumbnail_url,
                notes=notes,
                is_featured=is_featured,
                added_by=user if user.is_authenticated else None,
            )
            lapangan.save()

            return JsonResponse({"status": "success", "message": "Lapangan berhasil dibuat"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Format JSON tidak valid"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

#@login_required
def show_my_lapangan_json(request):
    my_lapangan = LapanganPadel.objects.filter(added_by=request.user)
    data = serializers.serialize(
        "json",
        my_lapangan,
        fields=(
            'place_id', 'nama', 'alamat', 'rating', 'total_review',
            'thumbnail_url', 'notes', 'is_featured', 'created_at', 'updated_at', 'added_by'
        )
    )
    return HttpResponse(data, content_type="application/json")
        
