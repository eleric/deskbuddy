from django.contrib import admin
from django.core.files.base import ContentFile

from .models import Photo
from django.conf import settings
from django.core.files import File
import os
from deskbuddy.persistence import get_storage_obj

# Register your models here.
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        storage = get_storage_obj()

        storage.save(request.FILES['photo'], obj.photo.name)

        photo = Photo()
        photo.title = obj.photo.name
        photo.photo = None
        photo.save()

        # super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        storage = get_storage_obj()

        if obj.photo.name is None or len(obj.photo.name) == 0:
            name = obj.title
        else:
            name = obj.photo.name

        try:
            storage.delete(name)
        except FileNotFoundError as e:
            print(f'Warning File not found.  {e}')

        super().delete_model(request, obj)
