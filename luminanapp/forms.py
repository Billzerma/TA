from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Gallery
from .models import Profile
from .models import Comment

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
        fields = ['title',  'thumbnail','description']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture', 'bio', 'phone', 'location',
            'instagram_link', 'facebook_link', 'x_link' # Tambahkan ini
        ]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tulis komentar Anda di sini...',
            }),
        }
        labels = {
            'content': 'Tulis Komentar',
        }