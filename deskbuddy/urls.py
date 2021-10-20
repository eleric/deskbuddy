from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('photos', views.photos, name='photos'),
    path('photo/<str:path>', views.photo, name='photo'),
]
