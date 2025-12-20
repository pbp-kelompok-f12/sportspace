from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from home.models import LapanganPadel
from .models import Review
from .forms import ReviewForm, EditReviewForm
from django.http import JsonResponse
import json
import requests
from django.http import HttpResponse

# review/views.py
@login_required
def add_review(request, lapangan_id):
    lapangan = get_object_or_404(LapanganPadel, id=lapangan_id)
    existing_review = Review.objects.filter(user=request.user, lapangan=lapangan).first()

    if existing_review:
        messages.error(request, "You have already reviewed this court. Edit your review instead.")
        return redirect('review:my_reviews')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.lapangan = lapangan
            review.rating = lapangan.rating  
            review.save()
            return redirect('review:my_reviews')
    else:
        form = ReviewForm()

    return render(request, "add_review.html", {"form": form, "lapangan": lapangan})

@login_required
def all_reviews(request, id):
    lapangan = get_object_or_404(LapanganPadel, pk=id)
    reviews = Review.objects.filter(lapangan=lapangan).order_by('-created_at')

    # Form logic
    if request.method == "POST":
        form = ReviewForm(request.POST, user=request.user)  
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.lapangan = lapangan  
            review.rating = lapangan.rating
            review.save()
            return redirect('review:all_reviews', id=id)
    else:
        form = ReviewForm(user=request.user)

    return render(request, "all_reviews.html", {
        "lapangan": lapangan,
        "reviews": reviews,
        "form": form,
    })
    
@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, user=request.user)
        if form.is_valid():
            lapangan = form.cleaned_data["lapangan"]
            if Review.objects.filter(user=request.user, lapangan=lapangan).exists():
                messages.error(request, f"You already reviewed {lapangan.nama}. You can only edit it.")
            else:
                review = form.save(commit=False)
                review.user = request.user
                review.lapangan = lapangan
                review.rating = lapangan.rating  
                review.save()
                messages.success(request, "Review added successfully!")
                return redirect("review:my_reviews")
    else:
        form = ReviewForm(user=request.user)

    return render(request, "my_reviews.html", {"reviews": reviews, "form": form})

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        review.comment = data.get("comment", review.comment)

        anon_val = data.get("anonymous", review.anonymous)
        if isinstance(anon_val, str):  # convert string "true"/"false" ke boolean
            anon_val = anon_val.lower() == "true"
        review.anonymous = bool(anon_val)

        review.save()
        return JsonResponse({
            "success": True,
            "comment": review.comment,
            "anonymous": review.anonymous
        })
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == "POST":
        review.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request"}, status=400)

from django.views.decorators.csrf import csrf_exempt
import requests
# ============================================
# API Flutter JSON Responses
# ============================================

def serialize_review(request, review):
    # Helper untuk format object Review ke JSON dictionary
    venue_image = ""
    if review.lapangan.thumbnail_url:
        venue_image = review.lapangan.thumbnail_url

    reviewer_image = ""
    if not review.anonymous:
        if hasattr(review.user, 'profile') and review.user.profile.photo_url:
             reviewer_image = review.user.profile.photo_url

    return {
        'id': review.id,
        'venue_name': review.lapangan.nama,
        'venue_image': venue_image,
        'reviewer_name': "Anonymous" if review.anonymous else review.user.username,
        'reviewer_image': reviewer_image if not review.anonymous else "",
        'rating': float(review.rating),
        'comment': review.comment,
        'is_anonymous': review.anonymous,
        'reviewed_at': review.created_at.strftime("%Y-%m-%d"),
    }

@login_required
def api_my_reviews(request):
    # API: Ambil daftar review milik user yang sedang login
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    data = [serialize_review(request, r) for r in reviews]
    return JsonResponse(data, safe=False)

@login_required
def api_venue_reviews(request, lapangan_id):
    # API: Ambil daftar review untuk lapangan tertentu
    lapangan = get_object_or_404(LapanganPadel, id=lapangan_id)
    reviews = Review.objects.filter(lapangan=lapangan).order_by('-created_at')
    data = [serialize_review(request, r) for r in reviews]
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def api_create_review(request):
    # API: Buat review baru (validasi input & cek duplikasi review)
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            lapangan_id = data.get("lapangan_id")
            comment = data.get("comment")
            anonymous = data.get("anonymous", False)

            if not lapangan_id or not comment:
                return JsonResponse({'error': 'Data incomplete'}, status=400)

            lapangan = get_object_or_404(LapanganPadel, id=lapangan_id)

            if Review.objects.filter(user=request.user, lapangan=lapangan).exists():
                return JsonResponse({'error': 'You have already reviewed this court'}, status=400)

            review = Review.objects.create(
                user=request.user,
                lapangan=lapangan,
                rating=lapangan.rating,
                comment=comment,
                anonymous=anonymous
            )
            return JsonResponse({"status": "success", "message": "Review saved"}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_update_review(request, pk):
    # API: Update komentar atau status anonymous pada review
    if request.method == "POST":
        review = get_object_or_404(Review, pk=pk, user=request.user)
        try:
            data = json.loads(request.body.decode("utf-8"))
            review.comment = data.get("comment", review.comment)
            review.anonymous = data.get("anonymous", review.anonymous)
            review.save()
            return JsonResponse({"status": "success", "message": "Review updated"})
        except:
             return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_delete_review(request, pk):
    # API: Hapus review spesifik milik user
    if request.method == "POST":
        review = get_object_or_404(Review, pk=pk, user=request.user)
        review.delete()
        return JsonResponse({"status": "success", "message": "Review deleted"})
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def proxy_image(request):
    # Helper: Proxy gambar eksternal untuk mengatasi masalah CORS/SSL di Flutter
    url = request.GET.get('url')

    if not url:
        return HttpResponse(status=404)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # verify=False digunakan untuk menembus SSL error di local environment
        response = requests.get(url, headers=headers, stream=True, timeout=5, verify=False)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            return HttpResponse(response.content, content_type=content_type)
        else:
            return HttpResponse(status=404)

    except Exception as e:
        return HttpResponse(status=404)

@login_required
def api_get_unreviewed_venues(request):
    # API: List lapangan yang BELUM direview user (untuk dropdown pilihan)
    reviewed_venue_ids = Review.objects.filter(user=request.user).values_list('lapangan_id', flat=True)
    unreviewed_venues = LapanganPadel.objects.exclude(id__in=reviewed_venue_ids)
    
    data = []
    for venue in unreviewed_venues:
        data.append({
            'id': venue.id,
            'name': venue.nama,
        })
        
    return JsonResponse(data, safe=False)