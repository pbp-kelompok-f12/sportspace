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

@login_required(login_url='/login')
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

@login_required(login_url='/login')
def create_venue(request):
    form = VenueForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        venue_entry = form.save(commit=False)

        if hasattr(venue_entry, 'user'):
            venue_entry.user = request.user

        venue_entry.save()
        return redirect('main:show_main')

    context = {'form': form}
    return render(request, "create_venue.html", context)

@login_required(login_url='/login')
def show_list_venue(request, id):
    venue = get_object_or_404(Venue, pk=id)
    reviews = venue.reviews.all().order_by("-created_at")

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
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been successfully created!")
            return redirect("main:login")

    context = {"form": form}
    return render(request, "register.html", context)

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST) 
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
    else:
        form = AuthenticationForm(request)

    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

@login_required(login_url='/login')
def edit_venue(request, id):
    venue = get_object_or_404(Venue, pk=id)
    form = VenueForm(request.POST or None, instance=venue)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('main:show_main')

    context = {'form': form, 'venue': venue}
    return render(request, "edit_venue.html", context)

@login_required(login_url='/login')
def delete_venue(request, id):
    venue = get_object_or_404(Venue, pk=id)

    if venue.owner != request.user:
        return HttpResponseRedirect(reverse('main:show_main'))

    venue.delete()
    return HttpResponseRedirect(reverse('main:show_main'))