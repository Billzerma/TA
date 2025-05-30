from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class Gallery(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=100, blank=True)
    thumbnail =  models.TextField()
    ig = models.URLField()
    fb = models.URLField()
    xtwt = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

class Style(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Artwork(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image_url = models.TextField()
    year = models.IntegerField(blank=True, null=True)
    media = models.CharField(max_length=100, blank=True)
    dimension = models.CharField(max_length=50, null=True, blank=True)
    artist = models.CharField(max_length=50, null=True, blank=True)
    contact_artist= models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ViTPrediction(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    predicted_style = models.ForeignKey(Style, on_delete=models.CASCADE)
    confidence_score = models.FloatField()
    model_version = models.CharField(max_length=50)
    predicted_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

