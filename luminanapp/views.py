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
from .models import Gallery
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
                return redirect('galeriSaya')
            elif user.groups.filter(name='visitor').exists():
                return redirect('home')
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
    return render(request, 'luminance/galeri.html')

def detailGaleri_view(request):
    return render(request, 'luminance/detailGaleri.html')

def detailKarya_view(request):
    return render(request, 'luminance/detailKarya.html')

@login_required
def dashboard_view(request):
    return render(request, 'luminance/dashboard.html')

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

    # --- Tambahkan logika ini untuk ambil karya berdasarkan style ---
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

    # ---------------------------------------------------------------

    context = {
        'gallery': galeri,
        'karya_per_style': karya_per_style,
    }

    return render(request, 'luminance/editGaleri.html', context)


