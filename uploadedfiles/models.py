from django.db import models
import django_filters
from django_filters.rest_framework import FilterSet
from .s3_storage import PublicMediaStorage


class UploadedFile(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    fname = models.FileField(max_length=512, unique=True,storage=PublicMediaStorage())
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-fname',)

    def __str__(self):
        return self.fname.name
