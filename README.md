# Django Setup

## Steps

1. Set permissions on directory

    ```
    sudo setfacl -m u:26:-wx  ./postgres/data # 26 is the postgres user id from the container image
    ```

1. Start your postgres container

    ```
    podman run -d -v ./postgres/data:/var/lib/pgsql/data:Z --name postgresql_database -e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db -p 5432:5432 rhel8/postgresql-13
    ```

1. Create the project

    ```
    django-admin startproject chris_django_project
    ```


1. Go into the setting.py file and set the database connection

    ```json
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'db',                      
            'USER': 'user',
            'PASSWORD': 'pass',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
    ```

1. Create the uploadedfiles application

    ```
    python manage.py startapp uploadedfiles
    ```

1. Allow access to the admin console by running

    ```
    django-admin manage.py migrate
    ```


1. Create super user for admin console

    ```
     python manage.py createsuperuser # Mine is 'chris' and password 'chris1234'
    ```

1. Create the UploadedFile model in the models.py in the uploadedfile application folder

1. Create the "api.py" file with the following content:

    ```python
    from django.urls import path, re_path, include
    from rest_framework.urlpatterns import format_suffix_patterns
    from uploadedfiles import views as uploadedfile_views

    urlpatterns = format_suffix_patterns([
        path('v1/uploadedfiles/',
             uploadedfile_views.UploadedFileList.as_view(),
             name='uploadedfile-list'),
        path('v1/uploadedfiles/<int:pk>/',
             uploadedfile_views.UploadedFileDetail.as_view(),
             name='uploadedfile-detail'),
    ]
    )
   ```

1. In the project url.py add the uploadedfile api.py reference to create paths for it

    ```
     url(r'^uploadedfiles/', include('uploadedfiles.api')),
    ```
   
1. Create the users application

    ```
     python manage.py startapp users
    ```


1. Setup **localstack**

     1. Run the localstack-compose.yaml file with `docker-compose -f localstack-compose.yaml up`

     1. Set the AWS environment variables

         ```
         export AWS_ACCESS_KEY_ID=foobar
         export AWS_SECRET_ACCESS_KEY=foobar
         ```

     1. Create your bucket `aws --endpoint-url=http://localhost:4566 s3 mb s3://chrisbucket`

     1. Set up the ACL policy for the bucket `aws --endpoint-url=http://localhost:4566 s3api put-bucket-acl --bucket chrisbucket --acl public-read-write`