from django.db import models
from django.contrib import admin
import uuid


# @admin.action(description='Mark selected stories as published')
# def make_published(modeladmin, request, queryset):
#     queryset.update(status='p')


class Photo(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    photo = models.FileField()

    def __str__(self):
        return self.title


class UserSettings(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100, null=True)
    photo_frequency = models.IntegerField(null=True)

    def __str__(self):
        string = f"{{'name': '{self.name}', 'photo_frequency': '{self.photo_frequency}'}}"
        return str(string)

