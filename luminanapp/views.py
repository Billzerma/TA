from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import Group
from .forms import RegisterForm  
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.shortcuts import redirect
from luminanapp.decorator import group_required

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
            user = form.save(commit=False)  # kita tangkap dulu user-nya
            user.save()  # simpan ke auth_user

            # Assign grup berdasarkan input checkbox
            if form.cleaned_data.get('is_gallery_owner'):
                group = Group.objects.get(name='gallery_owner')
            else:
                group = Group.objects.get(name='visitor')
            user.groups.add(group)

            login(request, user)  # login otomatis
            print("✅ User berhasil didaftarkan dan login:", user.username)
            return redirect('login')  # arahkan ke halaman home
        else:
            # Cetak error ke terminal untuk debugging
            print("❌ Form tidak valid:", form.errors)
    else:
        form = RegisterForm()
        
    return render(request, 'luminance/register.html', {'form': form})

def logout_view(request):
    logout(request)  # Hapus session login user
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


def manageGaleri_view(request):
    return render(request, 'luminance/manageGaleri.html')

def tambahGaleri_view(request):
    return render(request, 'luminance/tambahGaleri.html')


def editGaleri_view(request):
    return render(request, 'luminance/editGaleri.html')


