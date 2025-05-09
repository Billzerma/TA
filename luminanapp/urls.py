from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),  
    path('signup/', views.signup_view, name='signup'), 
    path('tentang/', views.tentang_view, name='tentang'), 
    path('galeri/', views.galeri_view, name='galeri'),
    path('onGaleri/', views.detailGaleri_view, name='onGaleri'),
     path('onKarya/', views.detailKarya_view, name='onKarya'),
]
