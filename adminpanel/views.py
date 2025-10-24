from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from accounts.models import Profile
from home.models import LapanganPadel
from home.forms import LapanganPadelForm
from booking.models import Booking
import json

# Helper untuk cek admin
def is_admin(user):
    return hasattr(user, 'profile') and user.profile.role == 'admin'

from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from django.http import JsonResponse

def create_admin_user(request):
    if request.method == 'POST':
        # Jika admin sudah ada, tampilkan pesan gagal
        if User.objects.filter(username='admin').exists():
            return render(request, 'admin_created_success.html', {
                'success': False,
                'message': 'User admin sudah ada.'
            })

        # Buat akun superuser baru
        User.objects.create_superuser(
            username='admin',
            email='seanmarcello836@gmail.com',
            password='cukurukuk'
        )
        return render(request, 'admin_created_success.html', {
            'success': True,
            'message': 'Akun admin berhasil dibuat!'
        })

    # Jika GET, tampilkan halaman konfirmasi
    return render(request, 'create_admin.html')


# ================= LAPANGAN =================

@login_required(login_url='/accounts/login/')
def dashboard(request):
    if request.user.profile.role != 'admin':
        return redirect('/home/')
    return render(request, 'dashboard_admin.html')


@login_required(login_url='/accounts/login/')
def dashboard_lapangan_ajax(request):
    if request.user.profile.role != 'admin':
        return redirect('/home/')
    return render(request, 'dashboard_admin_lapangan.html')


@login_required(login_url='/accounts/login/')
def get_lapangan_json(request):
    data = list(LapanganPadel.objects.values())
    return JsonResponse({'lapangan': data})


@csrf_exempt
@login_required(login_url='/accounts/login/')
def create_lapangan_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = LapanganPadelForm(data)
            if form.is_valid():
                lapangan = form.save()
                return JsonResponse({'success': True, 'id': lapangan.id})
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@login_required(login_url='/accounts/login/')
def update_lapangan_ajax(request, id):
    if request.method == 'POST':
        try:
            lapangan = get_object_or_404(LapanganPadel, id=id)
            data = json.loads(request.body)
            form = LapanganPadelForm(data, instance=lapangan)
            if form.is_valid():
                form.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@login_required(login_url='/accounts/login/')
def delete_lapangan_ajax(request, id):
    if request.method == 'DELETE':
        try:
            lapangan = get_object_or_404(LapanganPadel, id=id)
            lapangan.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ================= USER MANAGEMENT =================

@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
def dashboard_user_admin(request):
    """Halaman kelola akun pengguna"""
    return render(request, 'dashboard_admin_users.html')

@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
def get_users_json(request):
    """Ambil seluruh data user dan profil, bisa difilter berdasarkan role"""
    role_filter = request.GET.get('role', None)

    users = User.objects.all().select_related('profile')

    if role_filter and role_filter != 'all':
        users = users.filter(profile__role=role_filter)

    data = []
    for user in users:
        profile = getattr(user, 'profile', None)
        data.append({
            'id': user.id,
            'username': user.username,
            'email': profile.email if profile else '',
            'role': profile.role if profile else 'unknown',
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
        })
    return JsonResponse({'users': data})


@csrf_exempt
@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def add_user_ajax(request):
    """Tambah user baru"""
    try:
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email', '')
        role = data.get('role', 'customer')
        phone = data.get('phone', '')
        address = data.get('address', '')

        if not username:
            return JsonResponse({'status': 'error', 'message': 'Username wajib diisi'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username sudah digunakan'}, status=400)

        user = User.objects.create(username=username, email=email)
        profile = user.profile
        profile.role = role
        profile.phone = phone
        profile.address = address
        profile.email = email
        profile.save()

        return JsonResponse({'status': 'success', 'message': 'Pengguna berhasil ditambahkan'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def update_user_ajax(request, id):
    """Edit data pengguna"""
    try:
        user = User.objects.get(pk=id)
        profile = user.profile
        data = json.loads(request.body)

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.save()

        profile.role = data.get('role', profile.role)
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        profile.email = data.get('email', profile.email)
        profile.save()

        return JsonResponse({'status': 'success', 'message': 'Data pengguna berhasil diperbarui'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pengguna tidak ditemukan'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@login_required(login_url='/accounts/login/')
@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def delete_user_ajax(request, id):
    """Hapus user"""
    try:
        user = User.objects.get(pk=id)
        user.delete()
        return JsonResponse({'status': 'success', 'message': 'Pengguna berhasil dihapus'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Pengguna tidak ditemukan'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required(login_url='/accounts/login/')
def dashboard_booking_ajax(request):
    if request.user.profile.role != 'admin':
        return redirect('/home/')
    return render(request, 'dashboard_admin_bookings.html')

@login_required(login_url='/accounts/login/')
def get_booking_json(request):
    data = [
        {
            "id": str(b.id),
            "username": b.user.username,
            "venue_name": b.venue.name,
            "booking_date": b.booking_date.strftime("%Y-%m-%d"),
            "start_time": b.start_time.strftime("%H:%M"),
            "end_time": b.end_time.strftime("%H:%M"),
            "customer_name": b.customer_name,
            "customer_email": b.customer_email,
            "customer_phone": b.customer_phone,
        }
        for b in Booking.objects.select_related('user', 'venue').all()
    ]
    return JsonResponse({'bookings': data})

@csrf_exempt
@login_required(login_url='/accounts/login/')
def delete_booking_ajax(request, id):
    if request.method == 'DELETE':
        try:
            booking = Booking.objects.get(id=id)
            booking.delete()
            return JsonResponse({'success': True})
        except Booking.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)