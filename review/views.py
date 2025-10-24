from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from home.models import LapanganPadel
from .models import Review
from .forms import ReviewForm, EditReviewForm
from django.http import JsonResponse
import json

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
