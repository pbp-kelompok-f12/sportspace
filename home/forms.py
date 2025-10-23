# home/forms.py
from django import forms
from .models import LapanganPadel

class LapanganPadelForm(forms.ModelForm):
    class Meta:
        model = LapanganPadel
        fields = ['place_id', 'nama', 'alamat', 'rating', 'total_review', 
                  'thumbnail_url', 'notes', 'is_featured']
        
        widgets = {
            'place_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Google Maps Place ID'
            }),
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Lapangan'
            }),
            'alamat': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Alamat Lengkap'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '5'
            }),
            'total_review': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'thumbnail_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan internal (opsional)'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'place_id': 'Place ID',
            'nama': 'Nama Lapangan',
            'alamat': 'Alamat',
            'rating': 'Rating (0-5)',
            'total_review': 'Total Review',
            'thumbnail_url': 'URL Gambar',
            'notes': 'Catatan',
            'is_featured': 'Tampilkan di Recommended',
        }