from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from main.models import Venue
from .models import Review
from .forms import ReviewForm

@login_required
def add_review(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.venue = venue
            review.save()
            return redirect("main:venue_detail", venue_id=venue.id)
    else:
        form = ReviewForm()

    return render(request, "review/add_review.html", {"form": form, "venue": venue})

def show_reviews(request, venue_id):
    venue = get_object_or_404(Venue, pk=venue_id)
    reviews = venue.reviews.all().order_by("-created_at")
    return render(request, "review/show_reviews.html", {"venue": venue, "reviews": reviews})