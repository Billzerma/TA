from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import Group
from .forms import RegisterForm  
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.shortcuts import redirect
from luminanapp.decorator import group_required
from .forms import UploadGalleryForm
from .models import Gallery,Like, SaveArtGallery
from django.shortcuts import render, get_object_or_404, redirect
from .models import Gallery, Artwork, Style, ViTPrediction, Comment,GalleryVisit
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader
import torch
from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torchvision.transforms as transforms
import tempfile
import os
from django.conf import settings
from .forms import ProfileForm
from .models import Profile
from django.db.models import Count, Q
import random
from django.db.models import Prefetch
from .forms import CommentForm
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
import torch.nn.functional as F
import numpy as np


model_dir = os.path.join(settings.BASE_DIR, "luminanapp", "v2")

model = ViTForImageClassification.from_pretrained(model_dir)
processor = ViTImageProcessor.from_pretrained(model_dir)

def predict_style(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1).squeeze().numpy()

    predicted_class = np.argmax(probs)
    confidence = probs[predicted_class]
    label = model.config.id2label.get(predicted_class, None)

    # 🔁 Buat dict semua skor (gaya: persentase)
    all_confidences = {
        model.config.id2label[i]: float(f"{probs[i]*100:.2f}")
        for i in range(len(probs))
    }

    return label, confidence, all_confidences


def upload_artwork(request, pk):
    if request.method == "POST":
        gallery = get_object_or_404(Gallery, pk=pk)

        title = request.POST.get("title")
        year = request.POST.get("year")
        media = request.POST.get("media")
        dimension = request.POST.get("dimension")
        artist = request.POST.get("artist")
        contact_artist = request.POST.get("contact_artist")
        description = request.POST.get("description")
        image_file = request.FILES.get("image")

        # Upload ke Cloudinary
        uploaded_image = cloudinary.uploader.upload(image_file)
        image_url = uploaded_image['secure_url']

        # Simpan gambar sementara untuk prediksi
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_image_path = temp_file.name

        predicted_style_name, confidence, all_confidences = predict_style(temp_image_path)
        os.remove(temp_image_path)

        if predicted_style_name is None:
            predicted_style_name = "Unknown"
            confidence = 0.0

        style, _ = Style.objects.get_or_create(name=predicted_style_name)

        artwork = Artwork.objects.create(
            gallery=gallery,
            title=title,
            image_url=image_url,
            year=year,
            media=media,
            dimension=dimension,
            artist=artist,
            contact_artist=contact_artist,
            description= description,
        )

            # Simpan ke DB
        ViTPrediction.objects.create(
            artwork=artwork,
            predicted_style=style,
            confidence_score=confidence,
            model_version="ViT-B/16",
        )

        # 🔁 Tambahkan semua confidence ke pesan
        confidence_str = ", ".join([f"{k}: {v}%" for k, v in all_confidences.items()])
        messages.success(request, f"Karya berhasil diunggah. Gaya: {predicted_style_name} ({confidence * 100:.2f}%)<br>Confidence semua gaya: {confidence_str}")
        return redirect('editGaleri', pk=pk)

def hapus_karya(request, pk):
    karya = get_object_or_404(Artwork, pk=pk)
    karya.delete()
    messages.success(request, "Karya berhasil dihapus.")
    return redirect('editGaleri', pk=karya.gallery.pk)  # arahkan ke halaman edit galeri


def edit_karya(request, pk):
    karyaedit = get_object_or_404(Artwork, pk=pk)
    if request.method == "POST":
        karyaedit.title = request.POST.get("title")
        karyaedit.year = request.POST.get("year")
        karyaedit.media = request.POST.get("media")
        karyaedit.dimension = request.POST.get("dimension")
        karyaedit.artist = request.POST.get("artist")
        karyaedit.contact_artist = request.POST.get("contact_artist")
        karyaedit.description = request.POST.get("description")

        karyaedit.save()
        messages.success(request, "Karya berhasil diperbarui.")
        return redirect("editGaleri", pk=karyaedit.gallery.pk)

# view yang sudah diperbaiki
def hapus_galeri(request, pk):
    galeri = get_object_or_404(Gallery, pk=pk)
    if request.method == "POST":
        galeri.delete()
        messages.success(request, "Galeri berhasil dihapus.")
        # Arahkan ke halaman daftar galeri (misal: 'galeriSaya')
        return redirect("galeriSaya") 
    
    # Jika bukan POST, kembalikan ke halaman detail semula
    return redirect("editGaleri", pk=pk)


def is_gallery_owner(user):
    return user.groups.filter(name='gallery_owner').exists()

def home(request):
    
    semua_karya = list(Artwork.objects.all())
    random.shuffle(semua_karya)
    karya_list = semua_karya[:8]

   
    galeri_terpopuler = Gallery.objects.annotate(
        jumlah_like=Count('like', filter=Q(like__gallery__isnull=False))
    ).order_by('-jumlah_like')[:4]

    context = {
        'karya_list': karya_list,
        'galeri_terpopuler': galeri_terpopuler,
    }
    return render(request, 'luminance/home.html', context)




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # redirect sesuai grup
            if user.groups.filter(name='gallery_owner').exists():
                return redirect('profile')
            elif user.groups.filter(name='visitor').exists():
                return redirect('profile')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'luminance/log.html')



def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.save()  
            if form.cleaned_data.get('is_gallery_owner'):
                group = Group.objects.get(name='gallery_owner')
            else:
                group = Group.objects.get(name='visitor')
            user.groups.add(group)

            login(request, user)  
            print("✅ User berhasil didaftarkan dan login:", user.username)
            return redirect('login') 
        else:
            print("❌ Form tidak valid:", form.errors)
    else:
        form = RegisterForm()
        
    return render(request, 'luminance/register.html', {'form': form})

def logout_view(request):
    logout(request) 
    return redirect('login')


def tentang_view(request):
    return render(request, 'luminance/tentang.html')

def bantuan_view(request):
    return render(request, 'luminance/bantuan.html')

@login_required
def galeri_view(request):
    user = request.user

    liked_gallery_ids = set(
        Like.objects.filter(user=user, gallery__isnull=False).values_list('gallery_id', flat=True)
    )
    saved_gallery_ids = set(
        SaveArtGallery.objects.filter(user=user, gallery__isnull=False).values_list('gallery_id', flat=True)
    )

    galleries = Gallery.objects.all()

    context = {
        'galleries': galleries,
        'liked_gallery_ids': liked_gallery_ids,
        'saved_gallery_ids': saved_gallery_ids,
    }
    return render(request, 'luminance/galeri.html', context)


@login_required
def like_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    like, created = Like.objects.get_or_create(user=request.user, gallery=gallery)
    if not created:
        like.delete()
    return redirect('galeri')

@login_required
def save_gallery(request, gallery_id):
    gallery = get_object_or_404(Gallery, pk=gallery_id)
    save, created = SaveArtGallery.objects.get_or_create(user=request.user, gallery=gallery)
    if not created:
        save.delete()
    return redirect('galeri')

def like_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, pk=artwork_id)
   
    if request.user.is_authenticated:
       
        if Like.objects.filter(user=request.user, artwork=artwork).exists():
            
            Like.objects.filter(user=request.user, artwork=artwork).delete()
        else:
           
            Like.objects.create(user=request.user, artwork=artwork)

    return redirect('detail_karya', pk=artwork.pk)



def detailGaleri_view(request):
    return render(request, 'luminance/detailGaleri.html')

def detail_galeri_view(request, pk):
    gallery = get_object_or_404(Gallery, pk=pk)
    profile = Profile.objects.filter(user=gallery.owner).first()
    artworks = Artwork.objects.filter(gallery=gallery)

    TARGET_STYLES = ['Realism', 'Impressionism', 'Cubism', 'Romanticism', 'Expressionism']

    artworks_by_style = {}
    for artwork in artworks:
        vit_prediction = ViTPrediction.objects.filter(artwork=artwork).first()
        if vit_prediction and vit_prediction.predicted_style:
            style_name = vit_prediction.predicted_style.name
            if style_name in TARGET_STYLES:
                artworks_by_style.setdefault(style_name, []).append(artwork)
            else:
                artworks_by_style.setdefault("Tanpa Kategori", []).append(artwork)
        else:
            artworks_by_style.setdefault("Tanpa Kategori", []).append(artwork)

    context = {
        'gallery': gallery,
        'profile': profile,
        'artworks_by_style': artworks_by_style,
    }
    return render(request, 'luminance/detailGaleri.html', context)



def detailKarya_view(request):
    return render(request, 'luminance/detailKarya.html')


def detail_karya_view(request, pk):
    user = request.user
    artwork = get_object_or_404(Artwork, pk=pk)
    gallery = artwork.gallery
    profile = Profile.objects.filter(user=gallery.owner).first()

    all_artworks = list(Artwork.objects.filter(gallery=gallery).order_by('id'))
    current_index = all_artworks.index(artwork)

    prev_artwork = all_artworks[current_index - 1] if current_index > 0 else None
    next_artwork = all_artworks[current_index + 1] if current_index < len(all_artworks) - 1 else None

    liked_artwork_ids = set(
        Like.objects.filter(user=user, artwork__isnull=False).values_list('artwork_id', flat=True)
    )


    comments = Comment.objects.filter(artwork=artwork).order_by('-created_at')

    if request.method == 'POST':
       
        if not request.user.is_authenticated:
            return redirect('login') 

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.artwork = artwork
            new_comment.user = request.user
            new_comment.save()
            return redirect('detail_karya', pk=artwork.pk)
    else:
        # Jika bukan POST request, buat form kosong
        comment_form = CommentForm()

    context = {
        'artwork': artwork,
        'gallery': gallery,
        'profile': profile,
        'prev_artwork': prev_artwork,
        'next_artwork': next_artwork,
        'liked_artwork_ids': liked_artwork_ids,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'luminance/detailKarya.html', context)




@login_required
def manageGaleri_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    galleries = Gallery.objects.filter(owner=request.user)
    context = {
        'user': user,
        'profile': profile,
        'galleries':galleries
    }

    
    return render(request, 'luminance/manageGaleri.html', context)

def tambahGaleri_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == 'POST':
        form = UploadGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery = form.save(commit=False)
            gallery.owner = request.user
            gallery.save()
            return redirect('galeriSaya')  
    else:
        form = UploadGalleryForm()

        context = {
        'user': user,
        'profile': profile,
        'form':form
    }
        
    return render(request, 'luminance/tambahGaleri.html', context)



def editGaleri_view(request, pk):
    galeri = get_object_or_404(Gallery, pk=pk)
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        # Update gallery fields
        galeri.title = request.POST.get("title")
        galeri.description = request.POST.get("description")

        # Update thumbnail jika user upload file baru
        if 'thumbnail' in request.FILES:
            galeri.thumbnail = request.FILES['thumbnail']

        galeri.save()
        messages.success(request, "Perubahan galeri berhasil disimpan.")
        return redirect("editGaleri", pk=pk)

    karya = Artwork.objects.filter(gallery=galeri)

    target_styles = ['Realism', 'Impressionism', 'Cubism', 'Romanticism', 'Expressionism']
    styles = Style.objects.filter(name__in=target_styles)

    karya_per_style = {}
    for style in styles:
        karya_ids = ViTPrediction.objects.filter(
            artwork__in=karya,
            predicted_style=style
        ).values_list('artwork_id', flat=True)

        karya_per_style[style.name] = karya.filter(id__in=karya_ids)


    context = {
        'gallery': galeri,
        'karya_per_style': karya_per_style,
        'user': user,
        'profile': profile,
    }

    return render(request, 'luminance/editGaleri.html', context)

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    # Ambil grup user (role)
    roles = user.groups.values_list('name', flat=True)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil berhasil diperbarui.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    
    user_galleries = Gallery.objects.filter(owner=user)

    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'roles': roles,
        'user_galleries': user_galleries, # <-- Tambahkan ke context
    }
    return render(request, 'luminance/profile.html', context)



def update_foto(request):
    if request.method == "POST" and request.FILES.get("profile_picture"):
        profile = request.user.profile
        profile.profile_picture = request.FILES["profile_picture"]
        profile.save()
    return redirect("profile")  # Ganti dengan URL kamu

@login_required
def update_profile_details(request):
    if request.method == "POST":
        user = request.user # Dapatkan objek User
        profile = user.profile # Dapatkan objek Profile terkait
        profile = request.user.profile
        profile.phone = request.POST.get("phone", "")
        profile.location = request.POST.get("location", "")

        profile.instagram_link = request.POST.get("instagram_link", "")
        profile.facebook_link = request.POST.get("facebook_link", "")
        profile.x_link = request.POST.get("x_link", "")
        profile.bio = request.POST.get("bio", "")
        profile.save()
    return redirect("profile") 





@login_required
def get_gallery_stats_api(request, gallery_id):
    gallery = get_object_or_404(Gallery, pk=gallery_id)


    if gallery.owner != request.user:
        return HttpResponseForbidden("Anda tidak memiliki izin untuk melihat statistik ini.")


    total_likes = Like.objects.filter(gallery=gallery).count()


    style_names = ['Realism', 'Cubism', 'Impressionism', 'Expressionism','Romanticism']
    styles = Style.objects.filter(name__in=style_names)
    
    style_counts = styles.annotate(
        artwork_count=Count('vitprediction__artwork', 
                             filter=Q(vitprediction__artwork__gallery=gallery))
    ).values('name', 'artwork_count').order_by('name')

    pie_chart_data = {
        'labels': [item['name'] for item in style_counts],
        'data': [item['artwork_count'] for item in style_counts],
    }


    one_year_ago = datetime.now() - timedelta(days=365)
    monthly_visits = GalleryVisit.objects.filter(
        gallery=gallery,
        visited_at__gte=one_year_ago
    ).annotate(
        month=TruncMonth('visited_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')


    month_labels = [(datetime.now() - timedelta(days=30*i)).strftime("%b %Y") for i in range(12)]
    month_labels.reverse()
    
    visit_data_map = {item['month'].strftime("%b %Y"): item['count'] for item in monthly_visits}
    
    area_chart_data = {
        'labels': month_labels,
        'data': [visit_data_map.get(label, 0) for label in month_labels]
    }


    data = {
        'gallery_title': gallery.title,
        'total_likes': total_likes,
        'pie_chart': pie_chart_data,
        'area_chart': area_chart_data,
    }
    return JsonResponse(data)
