from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import SignUpForm, ProfileForm
from .models import Profile

# SIGN UP
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect sesuai role
            role = user.profile.role
            if role == 'admin':
                return redirect('accounts:admin_dashboard')
            elif role == 'venue_owner':
                return redirect('accounts:venue_dashboard')
            else:
                return redirect('accounts:customer_dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


# LOGIN
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            role = user.profile.role

            if role == 'admin':
                return redirect('accounts:admin_dashboard')
            elif role == 'venue_owner':
                return redirect('accounts:venue_dashboard')
            else:
                return redirect('accounts:customer_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


# LOGOUT
def logout(request):
    logout(request)
    return redirect('accounts:login')

# DASHBOARD PER ROLE
@login_required
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')

@login_required
def venue_dashboard(request):
    return render(request, 'accounts/venue_dashboard.html')

@login_required
def customer_dashboard(request):
    return render(request, 'accounts/customer_dashboard.html')

# PROFILE
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'profile': request.user.profile})

# EDIT PROFILE
@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# JSON PROFILE (untuk AJAX)
@login_required
def profile_json(request):
    profile = request.user.profile
    data = {
        'username': request.user.username,
        'email': request.user.email,
        'role': profile.role,
        'phone': profile.phone,
        'address': profile.address,
    }
    return JsonResponse(data)