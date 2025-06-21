from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = CloudinaryField('image', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True) # Tambahkan ini
    location = models.CharField(max_length=100, blank=True, null=True)
    instagram_link = models.URLField(max_length=200, blank=True, null=True)
    facebook_link = models.URLField(max_length=200, blank=True, null=True)
    x_link = models.URLField(max_length=200, blank=True, null=True) # Untuk Twitter/X

    def __str__(self):
        return self.user.username

class Gallery(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    thumbnail = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Style(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Artwork(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image_url = CloudinaryField('image', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    media = models.CharField(max_length=100, blank=True)
    dimension = models.CharField(max_length=50, null=True, blank=True)
    artist = models.CharField(max_length=50, null=True, blank=True)
    contact_artist= models.CharField(max_length=50, null=True, blank=True)
    description= models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ViTPrediction(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    predicted_style = models.ForeignKey(Style, on_delete=models.CASCADE)
    confidence_score = models.FloatField()
    model_version = models.CharField(max_length=50)
    predicted_at = models.DateTimeField(auto_now_add=True)



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)



class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey('Artwork', on_delete=models.CASCADE, null=True, blank=True)
    gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.artwork and not self.gallery:
            raise ValidationError("Like harus memiliki salah satu: artwork atau gallery.")
        if self.artwork and self.gallery:
            raise ValidationError("Like tidak boleh punya dua target sekaligus.")

    def __str__(self):
        return f"Like by {self.user.username}"

class SaveArtGallery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey('Artwork', on_delete=models.CASCADE, null=True, blank=True)
    gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.artwork and not self.gallery:
            raise ValidationError("Harus menyimpan salah satu: artwork atau gallery.")
        if self.artwork and self.gallery:
            raise ValidationError("Tidak boleh menyimpan artwork dan gallery sekaligus.")

    def __str__(self):
        return f"Save by {self.user.username}"
    
class GalleryVisit(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='visits')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Opsional: catat siapa yang mengunjungi
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit to {self.gallery.title} at {self.visited_at.strftime('%Y-%m-%d %H:%M')}"