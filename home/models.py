# home/models.py
from django.db import models
from django.contrib.auth.models import User

class LapanganPadel(models.Model):
    place_id = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="Google Maps Place ID, untuk mencegah duplikat"
    )
    nama = models.CharField(max_length=200)
    alamat = models.CharField(max_length=300)
    rating = models.FloatField(null=True, blank=True)
    total_review = models.IntegerField(null=True, blank=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Additional fields untuk keperluan internal
    notes = models.TextField(blank=True, help_text="Catatan internal tentang lapangan ini")
    is_featured = models.BooleanField(default=False, help_text="Tampilkan di recommended")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lapangan Padel"
        verbose_name_plural = "Lapangan Padel"
        ordering = ['-rating', '-total_review']

    def __str__(self):
        return self.nama