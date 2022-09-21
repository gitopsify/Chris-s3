# Start the Application

## Steps

1. Stop the podman container if you have started the container

     ```
     podman stop postgresql_database
     ```

1. Remove the podman container if you have already started the container

     ```
     podman rm postgresql_database 
     ```

1. Remove the local directory for postgres if you have already started the container

    ```
    sudo rm -rf ./postgres/data/*
    ```

1. Start the postgres container (make sure you are in the directory of the **postgres** folder)

    ```
    podman run -d -v ./postgres/data:/var/lib/pgsql/data:Z --name postgresql_database -e POSTGRESQL_USER=user -e POSTGRESQL_PASSWORD=pass -e POSTGRESQL_DATABASE=db -p 5432:5432 rhel8/postgresql-13
    ```

1. Stop localstack if it isn't already

    ```
    docker-compose -f localstack-compose.yaml down
    ```

1. Delete the localstack directory

    ```
    sudo rm -rf /tmp/localstack
    ```

1. Start localstack

    ```
    docker-compose -f localstack-compose.yaml up
    ```

1. Keep the terminal running.  Open up a new terminal.

1. Create the django postgres database

    ```
    python manage.py migrate
    ```

1. Create the superuser **chris**

    ```
    python manage.py createsuperuser # Mine is 'chris' and password 'chris1234'
    ```

1. Set the AWS environment variables

    ```
    export AWS_ACCESS_KEY_ID=foobar
    export AWS_SECRET_ACCESS_KEY=foobar
    ```

1. Create the s3 bucket called **chrisbucket**

    ```
    aws --endpoint-url=http://localhost:4566 s3 mb s3://chrisbucket
    ```

1. Create the ACL policy for the s3 bucket

    ```
    aws --endpoint-url=http://localhost:4566 s3api put-bucket-acl --bucket chrisbucket --acl public-read-write
    ```

1. Start the django application by clicking on the run button in pycharm

1. Open up the browser to **http://127.0.0.1:8000/admin**

1. Login using the username **chris** and password **chris1234**

1. On a new terminal run the tests to upload and get a file:

    ```
     python manage.py test uploadedfiles.tests.test_storage.PublicMediaStorageTests.test_upload_object;
     python manage.py test uploadedfiles.tests.test_storage.PublicMediaStorageTests.test_ls;
     python manage.py test uploadedfiles.tests.test_storage.PublicMediaStorageTests.test_download_object;
     python manage.py test uploadedfiles.tests.test_storage.PublicMediaStorageTests.test_delete_object;
    ```

