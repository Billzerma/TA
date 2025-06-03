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
    gallery = get_object_or_404(Gallery, pk=pk)

    if request.method == "POST":
        # Update gallery fields
        gallery.title = request.POST.get("title")
        gallery.contact = request.POST.get("contact")
        gallery.location = request.POST.get("location")
        gallery.ig = request.POST.get("ig")
        gallery.fb = request.POST.get("fb")
        gallery.xtwt = request.POST.get("xtwt")
        gallery.description = request.POST.get("description")

        # Update thumbnail jika user upload file baru
        if 'thumbnail' in request.FILES:
            gallery.thumbnail = request.FILES['thumbnail']

        gallery.save()
        messages.success(request, "Perubahan galeri berhasil disimpan.")
        return redirect("editGaleri", pk=pk)  # Ganti dengan URL view-mu

    context = {"gallery": gallery}

    return render(request, 'luminance/editGaleri.html', {'gallery': gallery})


