from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from main.models import Field
from .models import Review
from .forms import ReviewForm

@login_required
def add_review(request, field_id):
    field = get_object_or_404(Field, pk=field_id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.field = field
            review.save()
            # setelah submit, balik ke halaman detail field
            return redirect("main:field_detail", field_id=field.id)
    else:
        form = ReviewForm()

    return render(request, "review/add_review.html", {"form": form, "field": field})

def show_reviews(request, field_id):
    field = get_object_or_404(Field, pk=field_id)
    reviews = field.reviews.all().order_by("-created_at")
    return render(request, "review/show_reviews.html", {"field": field, "reviews": reviews})