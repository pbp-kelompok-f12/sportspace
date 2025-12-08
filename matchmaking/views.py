from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Match 
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MatchSerializer 


# -----------------------------------------------
# --- VIEWS UNTUK FLUTTER (JSON API) ---
# -----------------------------------------------

@login_required
@api_view(['GET'])
def list_match_json(request):
    matches = Match.objects.all().order_by('-created_at')
    # Context{'request': request} diperlukan agar serializer tahu user yang sedang login
    serializer = MatchSerializer(matches, many=True, context={'request': request})
    return Response(serializer.data)

@login_required
@api_view(['GET'])
def detail_match_json(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    serializer = MatchSerializer(match, context={'request': request})
    return Response(serializer.data)


@login_required
@csrf_exempt
def create_1v1_flutter(request):
    if request.method == 'POST':
        if Match.objects.filter(players=request.user).exists():
            return JsonResponse({'status': 'error', 'message': "Anda sudah terdaftar di match lain."}, status=400)
            
        try:
            match = Match.objects.create(mode='1v1', created_by=request.user) 
            match.players.add(request.user)
            return JsonResponse({'status': 'success', 'message': "Match 1 vs 1 berhasil dibuat!"})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f"Gagal membuat match: {e}"}, status=400)
    return JsonResponse({'status': 'error', 'message': "Metode tidak diizinkan"}, status=405)


@login_required
@csrf_exempt
def create_2v2_flutter(request):
    if request.method == 'POST':
        if Match.objects.filter(players=request.user).exists():
            return JsonResponse({'status': 'error', 'message': "Anda sudah terdaftar di match lain."}, status=400)
            
        try:
            data = json.loads(request.body)
            teammate_name = data.get('teammate', '')  
            
            if not teammate_name:
                return JsonResponse({'status': 'error', 'message': "Nama teman tidak boleh kosong."}, status=400)

            match = Match.objects.create(mode='2v2', created_by=request.user, temp_teammate=teammate_name)
            match.players.add(request.user)
            return JsonResponse({'status': 'success', 'message': f"Match 2 vs 2 berhasil dibuat dengan teman '{teammate_name}'!"})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f"Gagal membuat match: {e}"}, status=400)
    return JsonResponse({'status': 'error', 'message': "Metode tidak diizinkan"}, status=405)


@login_required
@csrf_exempt
def join_match_flutter(request, match_id):
    if request.method == 'POST':
        match = get_object_or_404(Match, id=match_id)
        user = request.user # Sudah login_required, jadi user pasti ada.

        is_registered = match.players.filter(pk=user.pk).exists()

        if is_registered:
            return JsonResponse({'status': 'info', 'message': "Anda sudah terdaftar di match ini."})
        
        # --- PERBAIKAN LOGIKA JOIN ---
        
        # Cek Double-Booking: User tidak boleh terdaftar di Match lain
        if Match.objects.filter(players=user).exclude(pk=match_id).exists():
            return JsonResponse({'status': 'error', 'message': "Anda sudah terdaftar di match lain yang aktif."}, status=400)
        
        # Cek apakah ada slot dan user bukan creator
        if match.can_join() and match.created_by != user:
            match.players.add(user)
            return JsonResponse({'status': 'success', 'message': "Berhasil bergabung ke match."})
        else:
            message = "Match sudah penuh."
            if match.created_by == user:
                message = "Anda adalah pembuat match ini."
            
            return JsonResponse({'status': 'error', 'message': message}, status=400)
    
    return JsonResponse({'status': 'error', 'message': "Metode tidak diizinkan"}, status=405)


@login_required
@csrf_exempt
def delete_match_flutter(request, match_id):
    if request.method == 'POST':
        match = get_object_or_404(Match, id=match_id)

        if match.created_by == request.user:
            # Menggunakan .delete() sesuai dengan model Anda
            match.delete() 
            return JsonResponse({'status': 'success', 'message': "Match berhasil dihapus."})
        else:
            return JsonResponse({'status': 'error', 'message': "Anda tidak memiliki izin untuk menghapus match ini."}, status=403)
            
    return JsonResponse({'status': 'error', 'message': "Metode tidak diizinkan"}, status=405)