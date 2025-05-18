from django.shortcuts import render

def home(request):
    return render(request, 'luminance/home.html')

def login_view(request):
    return render(request, 'luminance/log.html')

def register_view(request):
    return render(request, 'luminance/register.html')

def tentang_view(request):
    return render(request, 'luminance/tentang.html')

def galeri_view(request):
    return render(request, 'luminance/galeri.html')

def detailGaleri_view(request):
    return render(request, 'luminance/detailGaleri.html')

def detailKarya_view(request):
    return render(request, 'luminance/detailKarya.html')

def dashboard_view(request):
    return render(request, 'luminance/dashboard.html')

def manageGaleri_view(request):
    return render(request, 'luminance/manageGaleri.html')

def tambahGaleri_view(request):
    return render(request, 'luminance/tambahGaleri.html')

