# home/forms.py
from django import forms
from .models import LapanganPadel

class LapanganPadelForm(forms.ModelForm):
    # --- TAMBAHKAN METODE __init__ INI ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Jika form ini untuk instance yang sudah ada (mode edit)
        if self.instance and self.instance.pk:
            # Jadikan place_id read-only
            self.fields['place_id'].widget.attrs['readonly'] = True
            self.fields['place_id'].widget.attrs['style'] = 'background-color: #e9ecef;' # Beri warna abu-abu
        else:
            # Jika ini form baru (mode add), sembunyikan field place_id
            # Kita akan generate nilainya di view
            self.fields.pop('place_id')

    class Meta:
        model = LapanganPadel
        # Hapus 'place_id' dari sini karena kita atur secara dinamis di __init__
        fields = ['nama', 'alamat', 'rating', 'total_review', 
                  'thumbnail_url', 'notes', 'is_featured', 'place_id'] # Tetap ada untuk mode edit
        
        widgets = {
            'place_id': forms.TextInput(attrs={
                'class': 'form-control',
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
            'place_id': 'Place ID (Otomatis)',
            'nama': 'Nama Lapangan',
            'alamat': 'Alamat',
            'rating': 'Rating (0-5)',
            'total_review': 'Total Review',
            'thumbnail_url': 'URL Gambar',
            'notes': 'Catatan',
            'is_featured': 'Tampilkan di Recommended',
        }