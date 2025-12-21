import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Match
from .serializers import MatchSerializer


# =======================
# JSON API (FLUTTER)
# =======================

@login_required
@api_view(['GET'])
def list_match_json(request):
    matches = Match.objects.all()
    serializer = MatchSerializer(
        matches, many=True, context={'request': request}
    )
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
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)

    if Match.objects.filter(players=request.user).exists():
        return JsonResponse(
            {'status': 'error', 'message': 'Anda sudah terdaftar di match lain.'},
            status=400,
        )

    match = Match.objects.create(mode='1v1', created_by=request.user)
    match.players.add(request.user)

    return JsonResponse({'status': 'success'})


@login_required
@csrf_exempt
def create_2v2_flutter(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)

    if Match.objects.filter(players=request.user).exists():
        return JsonResponse(
            {'status': 'error', 'message': 'Anda sudah terdaftar di match lain.'},
            status=400,
        )

    try:
        data = json.loads(request.body)
        teammate = data.get('teammate')
    except Exception:
        return JsonResponse({'status': 'error'}, status=400)

    if not teammate:
        return JsonResponse(
            {'status': 'error', 'message': 'Nama teman wajib diisi.'},
            status=400,
        )

    match = Match.objects.create(
        mode='2v2', created_by=request.user, temp_teammate=teammate
    )
    match.players.add(request.user)

    return JsonResponse({'status': 'success'})


@login_required
@csrf_exempt
def join_match_flutter(request, match_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)

    match = get_object_or_404(Match, pk=match_id)
    user = request.user

    if match.players.filter(pk=user.pk).exists():
        return JsonResponse({'status': 'info', 'message': 'Sudah terdaftar.'})

    if Match.objects.filter(players=user).exclude(pk=match_id).exists():
        return JsonResponse(
            {'status': 'error', 'message': 'Sudah ikut match lain.'},
            status=400,
        )

    if not match.can_join() or match.created_by == user:
        return JsonResponse(
            {'status': 'error', 'message': 'Tidak bisa join match.'},
            status=400,
        )

    match.players.add(user)
    return JsonResponse({'status': 'success'})


@login_required
@csrf_exempt
def delete_match_flutter(request, match_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=405)

    match = get_object_or_404(Match, pk=match_id)

    if match.created_by != request.user:
        return JsonResponse(
            {'status': 'error', 'message': 'Tidak memiliki izin.'},
            status=403,
        )

    match.delete()
    return JsonResponse({'status': 'success'})


# =======================
# WEB VIEWS (DUMMY)
# =======================

@login_required
def matchmaking_home(request):
    matches = Match.objects.all()
    return render(request, 'matchmaking.html', {'matches': matches})


@login_required
def one_vs_one(request):
    return render(request, 'one_vs_one.html')


@login_required
def two_vs_two(request):
    return render(request, 'two_vs_two.html')


@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    return render(request, 'match_detail.html', {'match': match})


@login_required
def join_match(request, match_id):
    return redirect('matchmaking:home')


@login_required
def delete_match(request, match_id):
    return redirect('matchmaking:home')
