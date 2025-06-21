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
    path('galeri/<int:gallery_id>/like/', views.like_gallery, name='like_gallery'),
    path('galeri/<int:gallery_id>/save/', views.save_gallery, name='save_gallery'),


    path('onGaleri/', views.detailGaleri_view, name='onGaleri'),
    path('galeri/<int:pk>/', views.detail_galeri_view, name='detail_galeri'),

    path('onKarya/', views.detailKarya_view, name='onKarya'),
    path('karya/<int:pk>/', views.detail_karya_view, name='detail_karya'),
    path('karya/<int:artwork_id>/like/', views.like_artwork, name='like_artwork'),
    
    path('galeriSaya/', views.manageGaleri_view, name='galeriSaya'),
    path('tambahGaleri/', views.tambahGaleri_view, name='tambahGaleri'),
    path('profile/', views.profile_view, name='profile'),
    path('profil/update-foto/', views.update_foto, name='update_foto'),

    path('api/stats/gallery/<int:gallery_id>/', views.get_gallery_stats_api, name='api_gallery_stats'),
    
    path('profile/update_details/', views.update_profile_details, name='update_profile_details'),
    path('galeri/<int:pk>/edit/', views.editGaleri_view, name='editGaleri'),
    path('galeri/<int:pk>/edit/upload-artwork/', views.upload_artwork, name='upload_artwork'),
    path('karya/<int:pk>/hapus/', views.hapus_karya, name='hapus_karya'),
    path("karya/<int:pk>/edit/", views.edit_karya, name="edit_karya"),
    path("galeri/hapus/<int:pk>/", views.hapus_galeri, name="hapus_galeri"),
    path('logout/', views.logout_view, name='logout'),
]
