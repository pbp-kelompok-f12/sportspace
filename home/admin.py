from django.contrib import admin
from .models import LapanganPadel

@admin.register(LapanganPadel)
class LapanganPadelAdmin(admin.ModelAdmin):
    # Kolom yang ditampilkan di daftar admin
    list_display = (
        'nama',
        'alamat',
        'rating',
        'total_review',
        'is_featured',
        'created_at',
        'updated_at'
    )

    # Kolom yang dapat dicari
    search_fields = ('nama', 'alamat', 'place_id')

    # Filter di sisi kanan admin (misalnya filter featured)
    list_filter = ('is_featured',)

    # Urutan default di tabel admin
    ordering = ('-rating', '-total_review')

    # Semua field dibuat hanya bisa dibaca
    readonly_fields = (
        'place_id',
        'nama',
        'alamat',
        'rating',
        'total_review',
        'thumbnail_url',
        'notes',
        'is_featured',
        'created_at',
        'updated_at'
    )

    # Nonaktifkan operasi CRUD (Add/Edit/Delete)
    def has_add_permission(self, request):
        return False  # Tidak bisa menambah data

    def has_change_permission(self, request, obj=None):
        return False  # Tidak bisa mengubah data

    def has_delete_permission(self, request, obj=None):
        return False  # Tidak bisa menghapus data
