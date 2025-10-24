from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Kolom yang tampil di daftar admin
    list_display = ('user', 'role', 'email', 'phone', 'address')

    # Field yang bisa dicari di search bar admin
    search_fields = ('user__username', 'email', 'phone', 'address', 'role')

    # Filter di sisi kanan admin (berdasarkan role)
    list_filter = ('role',)

    # Urutan default data di tabel admin
    ordering = ('user__username',)

    # Semua field hanya bisa dibaca (tidak bisa diedit)
    readonly_fields = ('user', 'role', 'email', 'phone', 'address', 'photo_url')

    # Menonaktifkan semua operasi CRUD di Django Admin
    def has_add_permission(self, request):
        return False  # Tidak bisa menambah data baru

    def has_change_permission(self, request, obj=None):
        return False  # Tidak bisa mengubah data

    def has_delete_permission(self, request, obj=None):
        return False  # Tidak bisa menghapus data
