from django.urls import path, re_path, include
from rest_framework.urlpatterns import format_suffix_patterns
from uploadedfiles import views as uploadedfile_views
from users import views as user_views

urlpatterns = format_suffix_patterns([
    path('api/v1/users/',
         user_views.UserCreate.as_view(), name='user-create'),

    path('api/v1/users/<int:pk>/',
         user_views.UserDetail.as_view(), name='user-detail'),
    path('api/v1/uploadedfiles/',
         uploadedfile_views.UploadedFileList.as_view(),
         name='uploadedfile-list'),
    path('api/v1/uploadedfiles/<int:pk>/',
         uploadedfile_views.UploadedFileDetail.as_view(),
         name='uploadedfile-detail'),
]
)

