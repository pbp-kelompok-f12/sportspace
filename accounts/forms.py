from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Masukkan email aktif Anda."
    )
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        label="Peran"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hapus help_text bawaan
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
       

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # simpan email juga
        if commit:
            user.save()
            role = self.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Hilangkan role jika tidak boleh diubah user biasa
        fields = ['phone', 'photo_url', 'address']
