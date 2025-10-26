from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import SignUpForm, ProfileForm
from .models import Profile, FriendRequest
from django.views.decorators.http import require_POST

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


@login_required
def profile_view(request):
    # Pastikan profile selalu ada
    profile, _ = Profile.objects.get_or_create(user=request.user)
    received_requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)
    friends = profile.friends.all()
    suggestions = (
        Profile.objects
        .filter(role="customer")
        .exclude(id=profile.id)
        .exclude(id__in=profile.friends.all())
        .order_by("?")[:15]  # acak biar dinamis
    )

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
                'bio': profile.bio,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    # GET request
    else:
        form = ProfileForm(instance=profile)
        return render(request, "profile.html", {
            "profile": profile,
            "friends": friends,
            "received_requests": received_requests,
            "suggestions": suggestions,
            "total_booking": profile.total_booking,
            "average_rating": profile.avg_rating,
            "joined_date": profile.joined_date.strftime("%d %b %Y"),
            "form": form,
        })

# JSON PROFILE (untuk AJAX)

@login_required
def profile_json(request):
    profile = request.user.profile
    return JsonResponse({
        'success': True,
        'message': 'Profil berhasil diperbarui!',
        'email': profile.email,
        'phone': profile.phone,
        'address': profile.address,
        'photo_url': profile.photo_url,
        'bio': profile.bio,
        'total_booking': profile.total_booking,
        'avg_rating': profile.avg_rating,
        'joined_date': profile.joined_date.strftime("%d %b %Y"),
    })


# FRIEND

from django.contrib.auth.models import User

@login_required
def send_friend_request(request):
    if request.method == "POST":
        username = request.POST.get("username")
        target_user = User.objects.filter(username=username).first()

        if not target_user:
            return JsonResponse({"success": False, "message": "User tidak ditemukan."})

        if target_user == request.user:
            return JsonResponse({"success": False, "message": "Tidak bisa menambahkan diri sendiri."})

        target_profile = target_user.profile
        user_profile = request.user.profile

        # === 1. Sudah berteman ===
        if target_profile in user_profile.friends.all():
            return JsonResponse({
                "success": True,
                "status": "friend",
                "username": target_user.username,
                "photo_url": target_profile.photo_url,
                "bio": target_profile.bio or "",
                "message": ""
            })

        # === 2. Ada request pending ===
        if FriendRequest.objects.filter(from_user=request.user, to_user=target_user).exists():
            return JsonResponse({
                "success": True,
                "status": "pending",
                "username": target_user.username,
                "photo_url": target_profile.photo_url,
                "bio": target_profile.bio or "",
                "message": ""
            })

        # === 3. Mode pencarian saja ===
        if "search_only" in request.POST:
            return JsonResponse({
                "success": True,
                "status": "found",
                "username": target_user.username,
                "photo_url": target_profile.photo_url,
                "bio": target_profile.bio or "",
                "message": ""
            })

        # === 4. Kirim permintaan baru ===
        FriendRequest.objects.create(from_user=request.user, to_user=target_user)
        return JsonResponse({
            "success": True,
            "status": "pending",
            "username": target_user.username,
            "photo_url": target_profile.photo_url,
            "bio": target_profile.bio or "",
            "message": f"Permintaan dikirim ke {target_user.username}."
        })

    return JsonResponse({"success": False, "message": "Gunakan metode POST."})

@login_required
@require_POST
def handle_friend_request(request):
    action = request.POST.get("action")
    from_user_id = request.POST.get("from_user_id")

    try:
        friend_request = FriendRequest.objects.get(to_user=request.user, from_user_id=from_user_id)
    except FriendRequest.DoesNotExist:
        return JsonResponse({"success": False, "message": "Permintaan tidak ditemukan."}, status=404)

    from_user_profile = friend_request.from_user.profile

    if action == "accept":
        friend_request.accept()
        return JsonResponse({
            "success": True,
            "message": f"Kamu sekarang berteman dengan {friend_request.from_user.username}.",
            "new_friend": {
                "username": friend_request.from_user.username,
                "photo_url": from_user_profile.photo_url or "/static/img/defaultprofile.png",
                "bio": from_user_profile.bio or "",
            }
        })

    elif action == "reject":
        friend_request.delete()
        return JsonResponse({
            "success": True,
            "message": "Permintaan pertemanan ditolak.",
            "new_friend": None
        })

    return JsonResponse({"success": False, "message": "Aksi tidak valid."})

@login_required
def friends_json(request):
    profile = request.user.profile
    friends = profile.friends.all()

    data = []
    for f in friends:
        data.append({
            "username": f.user.username,
            "photo_url": f.photo_url or "/static/img/defaultprofile.png",
            "bio": f.bio or "",
        })

    return JsonResponse({"friends": data})

@login_required
@require_POST
def unfriend(request):
    username = request.POST.get("username")

    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "User tidak ditemukan."}, status=404)

    profile = request.user.profile
    target_profile = target_user.profile

    # Cek apakah memang teman
    if target_profile in profile.friends.all():
        profile.friends.remove(target_profile)
        target_profile.friends.remove(profile)
        return JsonResponse({"success": True, "message": f"Kamu tidak lagi berteman dengan {username}."})
    else:
        return JsonResponse({"success": False, "message": "Kamu tidak berteman dengan user ini."}, status=400)

@login_required
def get_request_count(request):
    count = FriendRequest.objects.filter(to_user=request.user, is_accepted=False).count()
    return JsonResponse({"count": count})

@login_required
def get_friend_count(request):
    profile = request.user.profile
    count = profile.friends.count()
    return JsonResponse({"count": count})

@login_required
def get_friend_suggestions(request):
    profile = request.user.profile
    suggestions = (
        Profile.objects
        .filter(role="customer")
        .exclude(id=profile.id)
        .exclude(id__in=profile.friends.all())
        .order_by("?")[:15]
    )

    data = [
        {
            "username": s.user.username,
            "photo_url": s.photo_url or "/static/img/defaultprofile.png",
            "bio": s.bio or "Aktif bermain padel!",
        }
        for s in suggestions
    ]
    return JsonResponse({"suggestions": data})