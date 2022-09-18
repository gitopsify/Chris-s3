## Steps

1. Create your virtual environment and add the dependencies from the `chris-django-requirements.txt`

1. Source the virtual environment from the command line

    ```
     source <your virtual env folder>/bin/activate
    ```

1. Upgrade pip

    ```
    pip install --upgrade pip
    ```

1. Install the requirements

    ```
    pip install -r chris-djano-requirements.txt
    ```

1. Create the django project

    ```
    django-admin startproject chris_django_project
    ```

1. Create the django application **uploadfiles**

    ```
    python manage.py startapp uploadedfiles
    ```

1. Create the django applicatin **users**

    ```
    python manage.py startapp users
    ```

1. Change the permission of the folder you are going to mount for your postgres pod

    ```
    chown -R 26:26 ./postgres/data
    ```

1. Create the postgres database

    ```
    podman run --privileged -d -v ./postgres/data:/var/lib/pgsql/data:Z --name postgresql_database -e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db -p 5432:5432 redhat.registry.io/rhel8/postgresql-13
    ```

1. Create your model for uploadedfiles

    ```
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
    ```

1. Add the serializers.yaml in the uploadedfiles folder

    ```
    from rest_framework import serializers

    from .models import UploadedFile
    
    
    class UploadedFileSerializer(serializers.HyperlinkedModelSerializer):
        owner = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
        fname = serializers.FileField(use_url=False)
        fsize = serializers.ReadOnlyField(source='fname.size')
        upload_path = serializers.CharField(write_only=True)
    
        class Meta:
            model = UploadedFile
            fields = ('url', 'id', 'creation_date', 'upload_path', 'fname', 'fsize', 'owner')
    
        def validate_upload_path(self, upload_path):
            """
            Overriden to check whether the provided path is under <username>/<uploads>/.
            """
            # remove leading and trailing slashes
            upload_path = upload_path.strip(' ')
            user = self.context['request'].user
            prefix = '{}/{}/'.format(user.username, 'uploads')
            if not upload_path.startswith(prefix):
                error_msg = "File path must start with '%s'." % prefix
                raise serializers.ValidationError([error_msg])
            return upload_path
    
        def validate(self, data):
            """
            Overriden to attach the upload path to the owner object.
            """
            # remove upload_path as it is not part of the model and attach it to the owner obj
            upload_path = data.pop('upload_path')
            owner = self.context['request'].user
            owner.upload_path = upload_path
            data['owner'] = owner
            return data

    ```

1. Add the **uploadedfiles** and **users** to the setting.py for INSTALLED_APPS. Make sure you have a comma after
the last entry

1. Add the **users** serializers.py

  

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