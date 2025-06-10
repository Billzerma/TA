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
    path('galeriSaya/', views.manageGaleri_view, name='galeriSaya'),
    path('tambahGaleri/', views.tambahGaleri_view, name='tambahGaleri'),
    path('profile/', views.profile_view, name='profile'),
    path('profil/update-foto/', views.update_foto, name='update_foto'),
    path('profil/update-bio/', views.update_bio, name='update_bio'),
    path('galeri/<int:pk>/edit/', views.editGaleri_view, name='editGaleri'),
    path('galeri/<int:pk>/edit/upload-artwork/', views.upload_artwork, name='upload_artwork'),
    path('karya/<int:pk>/hapus/', views.hapus_karya, name='hapus_karya'),
    path("karya/<int:pk>/edit/", views.edit_karya, name="edit_karya"),
    path("galeri/hapus/<int:pk>/", views.hapus_galeri, name="hapus_galeri"),
    path('logout/', views.logout_view, name='logout'),
]
