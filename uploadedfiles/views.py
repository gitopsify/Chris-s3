from django.shortcuts import render

# Create your views here.
import logging

from django.conf import settings
from django.http import FileResponse
from rest_framework import generics, permissions
from rest_framework.reverse import reverse

from .models import UploadedFile
from .serializers import UploadedFileSerializer


class UploadedFileList(generics.ListCreateAPIView):
    """
    A view for the collection of uploaded user files.
    """
    http_method_names = ['get','post']
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer


class UploadedFileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    An uploaded file view.
    """
    http_method_names = ['get', 'put', 'delete']
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
