from django.db import models
import django_filters
from django_filters.rest_framework import FilterSet
from .s3_storage import PublicMediaStorage
from django.conf import settings


def uploaded_file_path(instance, filename):
    # file will be stored to Swift at:
    # SWIFT_CONTAINER_NAME/<username>/uploads/<upload_path>
    result = settings.AWS_STORAGE_BUCKET_NAME + "/"
    if instance.owner.upload_path != '':
        result = instance.owner.upload_path
    return result


class UploadedFile(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    fname = models.FileField(max_length=512, upload_to=uploaded_file_path, unique=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-fname',)

    def __str__(self):
        return self.fname.name
