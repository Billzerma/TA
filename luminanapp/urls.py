from django.urls import path
from . import views
from luminanapp.views import register_view

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),  
    path('register/', views.register_view, name='register'),
     
    path('tentang/', views.tentang_view, name='tentang'), 
    path('bantuan/', views.bantuan_view, name='bantuan'), 
    path('galeri/', views.galeri_view, name='galeri'),
    path('onGaleri/', views.detailGaleri_view, name='onGaleri'),
    path('onKarya/', views.detailKarya_view, name='onKarya'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('galeriSaya/', views.manageGaleri_view, name='galeriSaya'),
    path('tambahGaleri/', views.tambahGaleri_view, name='tambahGaleri'),
    path('galeri/<int:pk>/edit/', views.editGaleri_view, name='editGaleri'),
    path('galeri/<int:pk>/edit/upload-artwork/', views.upload_artwork, name='upload_artwork'),
    path('karya/<int:pk>/hapus/', views.hapus_karya, name='hapus_karya'),

    path('logout/', views.logout_view, name='logout'),
]
