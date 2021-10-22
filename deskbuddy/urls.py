from django.urls import path, include

from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('photos', views.photos, name='photos'),
    path('photo/<str:path>', views.photo, name='photo'),
]
