from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
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
            auth_login(request, user)
            return redirect('/home/')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


# LOGIN
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            role = user.profile.role

            if role == 'admin':
                return redirect('adminpanel:dashboard')
            else:
                return redirect('/home/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# LOGOUT
def logout(request):
    auth_logout(request)
    return redirect('accounts:login')

# # DASHBOARD PER ROLE
# @login_required
# def admin_dashboard(request):
#     return render(request, 'admin_dashboard.html')

@login_required
def profile_view(request):
    # Pastikan profile selalu ada
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Profil berhasil diperbarui!',
                'email': profile.email,
                'phone': profile.phone,
                'address': profile.address,
                'photo_url': profile.photo_url,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    # GET request
    else:
        form = ProfileForm(instance=profile)
        return render(request, 'profile.html', {
            'profile': profile,
            'form': form
        })


# @login_required
# def edit_profile(request):
#     # Ambil profil user yang sedang login
#     profile = request.user.profile

#     # Jika email di Profile masih kosong, isi dari User.email
#     if not profile.email:
#         profile.email = request.user.email

#     if request.method == 'POST':
#         # Ambil data POST dan isi ke instance profile yang sudah ada
#         form = ProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('accounts:profile') 
#     else:
#         # isi form dengan data lama
#         form = ProfileForm(instance=profile)

#     context = {'form': form}
#     return render(request, 'edit_profile.html', context)


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