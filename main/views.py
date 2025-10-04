import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render, redirect, get_object_or_404
from main.forms import FieldForm
from main.models import Field
from django.http import HttpResponse
from django.core import serializers

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

@login_required(login_url='/login')
def show_main(request):
    filter_type = request.GET.get("filter", "all")  # default 'all'

    if filter_type == "all":
        field_list = Field.objects.all()
    else:
        field_list = Field.objects.filter(vendor__owner=request.user)

    context = {
        'username': request.user.username,
        'field_list': field_list,
        'last_login': request.COOKIES.get('last_login', 'Never'),
    }
    return render(request, "main.html", context)

@login_required(login_url='/login')
def create_field(request):
    form = FieldForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        field_entry = form.save(commit=False)

        # Jika model Field punya atribut ForeignKey ke User (mis. user = FK(User))
        if hasattr(field_entry, 'user'):
            field_entry.user = request.user

        field_entry.save()
        return redirect('main:show_main')

    context = {'form': form}
    return render(request, "create_field.html", context)

@login_required(login_url='/login')
def show_field(request, id):
    field = get_object_or_404(Field, pk=id)

    context = {
        'field': field
    }

    return render(request, "field_detail.html", context)

def show_xml(request):
    field_list = Field.objects.all()
    xml_data = serializers.serialize("xml", field_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    field_list = Field.objects.all()
    json_data = serializers.serialize("json", field_list)
    return HttpResponse(json_data, content_type="application/json")

def show_xml_by_id(request, field_id):
    field_qs = Field.objects.filter(pk=field_id)
    if not field_qs.exists():
        return HttpResponse(status=404)
    xml_data = serializers.serialize("xml", field_qs)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json_by_id(request, field_id):
    try:
        field_item = Field.objects.get(pk=field_id)
    except Field.DoesNotExist:
        return HttpResponse(status=404)
    json_data = serializers.serialize("json", [field_item])
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
def edit_field(request, id):
    field = get_object_or_404(Field, pk=id)
    form = FieldForm(request.POST or None, instance=field)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('main:show_main')

    context = {'form': form, 'field': field}
    return render(request, "edit_field.html", context)

@login_required(login_url='/login')
def delete_field(request, id):
    field = get_object_or_404(Field, pk=id)

    if field.vendor and field.vendor.owner != request.user:
        return HttpResponseRedirect(reverse('main:show_main'))

    field.delete()
    return HttpResponseRedirect(reverse('main:show_main'))