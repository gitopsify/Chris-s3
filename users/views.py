from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializers import UserSerializer


class UserCreate(generics.ListCreateAPIView):
    http_method_names = ['get', 'post']
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateAPIView):
    http_method_names = ['get', 'put']
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        """
        Overriden to add required username before serializer validation.
        """
        user = self.get_object()
        request.data['username'] = user.username
        return super(UserDetail, self).update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        Overriden to update user's password and email when requested by a PUT request.
        """
        serializer.save(email=serializer.validated_data.get("email"))
        user = self.get_object()
        password = serializer.validated_data.get("password")
        user.set_password(password)
        user.save()
