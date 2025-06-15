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
from .models import Gallery, Artwork, Style, ViTPrediction
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
from django.db.models import Prefetch



model_dir = os.path.join(settings.BASE_DIR, "luminanapp", "vit-style-classification")

model = ViTForImageClassification.from_pretrained(model_dir)
processor = ViTImageProcessor.from_pretrained(model_dir)

def predict_style(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        predicted_class = outputs.logits.argmax(-1).item()
    
    label = model.config.id2label.get(predicted_class, None)
    return label

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

        predicted_style_name = predict_style(temp_image_path)
        os.remove(temp_image_path)  # Hapus file sementara

        if predicted_style_name is None:
            predicted_style_name = "Unknown"

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

        ViTPrediction.objects.create(
            artwork=artwork,
            predicted_style=style,
            confidence_score=1.0,
            model_version="ViT-B/16",
        )

        messages.success(request, "Karya berhasil diunggah dan diprediksi.")
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
    return render(request, 'luminance/home.html')

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



def detailGaleri_view(request):
    return render(request, 'luminance/detailGaleri.html')

def detail_galeri_view(request, pk):
    # Ambil galeri berdasarkan pk
    gallery = get_object_or_404(Gallery, pk=pk)

    # Ambil profil dari pemilik galeri
    profile = Profile.objects.filter(user=gallery.owner).first()

    # Ambil semua karya seni dalam galeri tersebut
    artworks = Artwork.objects.filter(gallery=gallery)

    # Target style yang ingin ditampilkan
    TARGET_STYLES = ['Realism', 'Impressionism', 'Cubism', 'Romanticism', 'Expressionism']

    # Kelompokkan karya berdasarkan style dari prediksi ViT
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
    artwork = get_object_or_404(Artwork, pk=pk)
    gallery = artwork.gallery
    profile = Profile.objects.filter(user=gallery.owner).first()

    all_artworks = list(Artwork.objects.filter(gallery=gallery).order_by('id'))
    current_index = all_artworks.index(artwork)

    prev_artwork = all_artworks[current_index - 1] if current_index > 0 else None
    next_artwork = all_artworks[current_index + 1] if current_index < len(all_artworks) - 1 else None

    context = {
        'artwork': artwork,
        'gallery': gallery,
        'profile': profile,
        'prev_artwork': prev_artwork,
        'next_artwork': next_artwork
    }
    return render(request, 'luminance/detailKarya.html', context)




@login_required
def manageGaleri_view(request):
    galleries = Gallery.objects.filter(owner=request.user)
    return render(request, 'luminance/manageGaleri.html', {'galleries': galleries})

def tambahGaleri_view(request):
    if request.method == 'POST':
        form = UploadGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            gallery = form.save(commit=False)
            gallery.owner = request.user
            gallery.save()
            return redirect('galeriSaya')  # Redirect ke halaman galeriSaya tanpa pk
    else:
        form = UploadGalleryForm()
    return render(request, 'luminance/tambahGaleri.html', {'form': form})



def editGaleri_view(request, pk):
    galeri = get_object_or_404(Gallery, pk=pk)

    if request.method == "POST":
        # Update gallery fields
        galeri.title = request.POST.get("title")
        galeri.contact = request.POST.get("contact")
        galeri.location = request.POST.get("location")
        galeri.ig = request.POST.get("ig")
        galeri.fb = request.POST.get("fb")
        galeri.xtwt = request.POST.get("xtwt")
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
    }

    return render(request, 'luminance/editGaleri.html', context)

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil berhasil diperbarui.")
            return redirect('profile')  # ganti dengan nama urlmu
    else:
        form = ProfileForm(instance=profile)

    context = {
        'user': user,
        'profile': profile,
        'form': form,
    }
    return render(request, 'luminance/profile.html', context)


def update_foto(request):
    if request.method == "POST" and request.FILES.get("profile_picture"):
        profile = request.user.profile
        profile.profile_picture = request.FILES["profile_picture"]
        profile.save()
    return redirect("profile")  # Ganti dengan URL kamu

@login_required
def update_bio(request):
    if request.method == "POST":
        profile = request.user.profile
        profile.bio = request.POST.get("bio", "")
        profile.save()
    return redirect("profile")