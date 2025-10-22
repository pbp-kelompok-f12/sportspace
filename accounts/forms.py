from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role = self.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
        return user
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'phone', 'photo', 'address']
