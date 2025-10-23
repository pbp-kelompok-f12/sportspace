import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render, redirect, get_object_or_404
from main.forms import VenueForm
from main.models import Venue
from django.http import HttpResponse
from django.core import serializers

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from review.forms import ReviewForm
from review.models import Review

def landing(request):
    return render(request, "landing.html")

@login_required(login_url='/accounts/login/')
def show_main(request):
    filter_type = request.GET.get("filter", "all")  # default 'all'

    if filter_type == "all":
        venue_list = Venue.objects.all()
    else:
        venue_list = Venue.objects.filter(vendor__owner=request.user)

    context = {
        'username': request.user.username,
        'venue_list': venue_list,
        'last_login': request.COOKIES.get('last_login', 'Never'),
    }
    return render(request, "main.html", context)

@login_required(login_url='/accounts/login/')
def create_field(request):
    form = FieldForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        venue_entry = form.save(commit=False)

        if hasattr(venue_entry, 'user'):
            venue_entry.user = request.user

        venue_entry.save()
        return redirect('main:show_main')

    context = {'form': form}
    return render(request, "create_venue.html", context)

@login_required(login_url='/accounts/login/')
def show_field(request, id):
    field = get_object_or_404(Field, pk=id)
    reviews = field.reviews.all().order_by("-created_at")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.venue = venue
            review.save()
            return redirect("main:show_list_venue", id=venue.id)
    else:
        form = ReviewForm()

    context = {
        'venue': venue,
        'reviews': reviews,
        'form': form,
    }

    return render(request, "venue_detail.html", context)

def show_xml(request):
    venue_list = Venue.objects.all()
    xml_data = serializers.serialize("xml", venue_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    venue_list = Venue.objects.all()
    json_data = serializers.serialize("json", venue_list)
    return HttpResponse(json_data, content_type="application/json")

def show_xml_by_id(request, venue_id):
    venue_qs = Venue.objects.filter(pk=venue_id)
    if not venue_qs.exists():
        return HttpResponse(status=404)
    xml_data = serializers.serialize("xml", venue_qs)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json_by_id(request, venue_id):
    try:
        venue_item = Venue.objects.get(pk=venue_id)
    except Venue.DoesNotExist:
        return HttpResponse(status=404)
    json_data = serializers.serialize("json", [venue_item])
    return HttpResponse(json_data, content_type="application/json")

def register(request):
    # Deprecated in favor of accounts app; keep for compatibility if referenced
    return redirect('accounts:signup')

def login_user(request):
    return redirect('accounts:login')

def logout_user(request):
    return redirect('accounts:logout')

@login_required(login_url='/accounts/login/')
def edit_field(request, id):
    field = get_object_or_404(Field, pk=id)
    form = FieldForm(request.POST or None, instance=field)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('main:show_main')

    context = {'form': form, 'venue': venue}
    return render(request, "edit_venue.html", context)

@login_required(login_url='/login/')
def delete_field(request, id):
    field = get_object_or_404(Field, pk=id)

    if venue.owner != request.user:
        return HttpResponseRedirect(reverse('main:show_main'))

    venue.delete()
    return HttpResponseRedirect(reverse('main:show_main'))