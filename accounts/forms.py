from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    # hanya tampilkan 2 role
    role = forms.ChoiceField(
        choices=[('customer', 'Customer'), ('venue_owner', 'Venue Owner')],
        label="Role"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']  # simpan email ke model User

        if commit:
            user.save()
            # role = self.cleaned_data['role']       # ambil role yang dipilih
            # Profile.objects.create(user=user, role=role)  # buat profil baru terhubung ke user
        return user
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['email', 'phone', 'address', 'photo_url']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': (
                    'form-control text-black border border-gray-300 w-full rounded-md p-2 '
                    'focus:border-[#F87E18] focus:ring-2 focus:ring-[#F87E18]/50 transition'
                ),
                'placeholder': 'Alamat Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': (
                    'form-control text-black border border-gray-300 w-full rounded-md p-2 '
                    'focus:border-[#F87E18] focus:ring-2 focus:ring-[#F87E18]/50 transition'
                ),
                'placeholder': 'Nomor Telepon'
            }),
            'address': forms.TextInput(attrs={
                'class': (
                    'form-control text-black border border-gray-300 w-full rounded-md p-2 '
                    'focus:border-[#F87E18] focus:ring-2 focus:ring-[#F87E18]/50 transition'
                ),
                'placeholder': 'Alamat'
            }),
            'photo_url': forms.URLInput(attrs={
                'class': (
                    'form-control text-black border border-gray-300 w-full rounded-md p-2 '
                    'focus:border-[#F87E18] focus:ring-2 focus:ring-[#F87E18]/50 transition'
                ),
                'placeholder': 'Link Foto Profil'
            }),
        }