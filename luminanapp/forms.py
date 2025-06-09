from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Gallery
from .models import Profile

class RegisterForm(UserCreationForm):
    is_gallery_owner = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UploadGalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title', 'contact', 'location', 'thumbnail', 'ig', 'fb', 'xtwt', 'description']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio']
