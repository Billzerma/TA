from django.shortcuts import render

def home(request):
    return render(request, 'luminance/home.html')

def login_view(request):
    return render(request, 'luminance/login.html')

def signup_view(request):
    return render(request, 'luminance/signup.html')

def tentang_view(request):
    return render(request, 'luminance/tentang.html')

def galeri_view(request):
    return render(request, 'luminance/galeri.html')

def detailGaleri_view(request):
    return render(request, 'luminance/detailGaleri.html')

def detailKarya_view(request):
    return render(request, 'luminance/detailKarya.html')
