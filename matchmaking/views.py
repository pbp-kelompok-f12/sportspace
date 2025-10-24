from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Match

@login_required
def matchmaking_home(request):
    matches = Match.objects.all().order_by('-created_at')
    return render(request, 'matchmaking/matchmaking.html', {'matches': matches})

@login_required
def one_vs_one(request):
    if request.method == 'POST':
        match = Match.objects.create(mode='1v1', created_by=request.user)
        match.players.add(request.user)
        messages.success(request, "✅ Match 1v1 berhasil dibuat!")
        return redirect('matchmaking:home')
    return render(request, 'matchmaking/one_vs_one.html')

@login_required
def two_vs_two(request):
    if request.method == 'POST':
        teammate_name = request.POST.get('teammate')

        # Buat match baru dengan mode 2v2
        match = Match.objects.create(mode='2v2', created_by=request.user)
        # Tambahkan pembuat match dan nama teman sebagai 'pemain'
        match.players.add(request.user)
        match.temp_teammate = teammate_name  # Simpan nama teman di field tambahan
        match.save()

        messages.success(request, f"✅ Match 2v2 berhasil dibuat dengan teman '{teammate_name}'!")
        return redirect('matchmaking:home')

    return render(request, 'matchmaking/two_vs_two.html')

@login_required
def join_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.user in match.players.all():
        messages.info(request, "Anda sudah terdaftar di match ini.")
    elif match.can_join() and request.user != match.created_by:
        match.players.add(request.user)
        # Update status penuh jika sudah mencapai batas
        if match.mode == '1v1' and match.players.count() >= 2:
            match.is_full = True
        elif match.mode == '2v2' and match.players.count() >= 4:
            match.is_full = True
        match.save()
        messages.success(request, "Berhasil bergabung ke match.")
    else:
        messages.error(request, "Match sudah penuh atau tidak dapat diikuti.")

    return redirect('matchmaking:home')

@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    return render(request, 'matchmaking/match_detail.html', {'match': match})

@login_required
def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if match.created_by == request.user:
        match.delete()
        messages.success(request, "Match berhasil dihapus.")
    else:
        messages.error(request, "Anda tidak memiliki izin untuk menghapus match ini.")
    return redirect('matchmaking:home')
