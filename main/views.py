# main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core import serializers
from main.models import Venue, Vendor
from main.forms import VenueForm
from review.forms import ReviewForm

# @login_required(login_url='/accounts/login/')
# def show_main(request):
#     """Main dashboard untuk melihat venues"""
#     filter_type = request.GET.get("filter", "all")

#     if filter_type == "all":
#         venue_list = Venue.objects.all()
#     else:
#         # Filter venues milik user (melalui vendor)
#         venue_list = Venue.objects.filter(vendor__owner=request.user)

#     context = {
#         'username': request.user.username,
#         'venue_list': venue_list,
#         'last_login': request.COOKIES.get('last_login', 'Never'),
#     }
#     return render(request, "main.html", context)


# @login_required(login_url='/accounts/login/')
# def create_venue(request):
#     """Create new venue"""
#     form = VenueForm(request.POST or None)

#     if request.method == 'POST' and form.is_valid():
#         venue = form.save(commit=False)
        
#         # Pastikan user punya vendor, kalau belum buat otomatis
#         vendor, created = Vendor.objects.get_or_create(
#             owner=request.user,
#             defaults={
#                 'name': f"{request.user.username}'s Venue",
#                 'email': request.user.email
#             }
#         )
#         venue.vendor = vendor
#         venue.save()
        
#         return redirect('main:show_main')

#     context = {'form': form}
#     return render(request, "create_venue.html", context)


# @login_required(login_url='/accounts/login/')
# def show_venue(request, id):
#     """Show venue detail with reviews"""
#     venue = get_object_or_404(Venue, pk=id)
#     reviews = venue.reviews.all().order_by("-created_at")

#     if request.method == "POST":
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.user = request.user
#             review.venue = venue
#             review.save()
#             return redirect("main:show_venue", id=venue.id)
#     else:
#         form = ReviewForm()

#     context = {
#         'venue': venue,
#         'reviews': reviews,
#         'form': form,
#     }

#     return render(request, "venue_detail.html", context)


# @login_required(login_url='/accounts/login/')
# def edit_venue(request, id):
#     """Edit existing venue"""
#     venue = get_object_or_404(Venue, pk=id)
    
#     # Pastikan user adalah owner dari venue
#     if venue.vendor.owner != request.user:
#         return HttpResponseRedirect(reverse('main:show_main'))
    
#     form = VenueForm(request.POST or None, instance=venue)

#     if request.method == 'POST' and form.is_valid():
#         form.save()
#         return redirect('main:show_main')

#     context = {'form': form, 'venue': venue}
#     return render(request, "edit_venue.html", context)


# @login_required(login_url='/accounts/login/')
# def delete_venue(request, id):
#     """Delete venue"""
#     venue = get_object_or_404(Venue, pk=id)

#     # Pastikan user adalah owner dari venue
#     if venue.vendor.owner != request.user:
#         return HttpResponseRedirect(reverse('main:show_main'))

#     venue.delete()
#     return HttpResponseRedirect(reverse('main:show_main'))
