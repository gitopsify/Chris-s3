import boto3
import botocore
from botocore.client import BaseClient
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import logging
import os
import time
from swiftclient.exceptions import ClientException

logger = logging.getLogger(__name__)

class PublicMediaStorage(S3Boto3Storage):

    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False
    default_acl = 'public-read-write'
    container_name = None
    conn_params = None
    _boto_session = None
    _boto_client = None

    def initialize(self):
        if self.container_name is not None:
            return
        self.container_name = settings.AWS_STORAGE_BUCKET_NAME
        self.conn_params = settings.AWS_S3_OBJECT_PARAMETERS
        # swift storage connection object
        self.create_container()

    def get_connection(self):
        """
        Connect to s3 storage and return the connection object.
        """
        self.initialize();
        if self._boto_client is not None:
            return self._boto_client
        self._boto_session = boto3.session.Session()
        for i in range(5):  # 5 retries at most
            try:

                self._boto_client = self._boto_session.client(
                    service_name='s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    # The next option is only required because my provider only offers "version 2"
                    # authentication protocol. Otherwise this would be 's3v4' (the default, version 4).
                    config=botocore.client.Config(signature_version='s3'),
                )
            except ClientException as e:
                logger.error(str(e))
                if i == 4:
                    raise  # give up
                time.sleep(0.4)
            else:
                return self._boto_client

    def create_container(self):
        """
        Create the storage container.
        """
        conn = self.get_connection()
        try:
            conn.create_bucket(Bucket=self.container_name)
        except ClientException as e:
            logger.error(str(e))
            raise

    def ls(self, path, **kwargs):
        """
        Return a list of objects in the s3 storage with the provided path
        as a prefix.
        """
        b_full_listing = kwargs.get('full_listing', True)
        #if not path.endswith('/'):
         #   path = path + '/'
        l_ls = []  # listing of names to return
        has_run = False
        if path:
            conn = self.get_connection()
            for i in range(5):
                if has_run:
                    continue
                try:
                    paginator = conn.get_paginator('list_objects_v2')
                    page_iterator = paginator.paginate(Bucket=self.container_name, Prefix=path)

                    for page in page_iterator:
                        print('Get s3 bucket page: ')
                        if page['KeyCount'] == 0:
                            continue
                        files = page["Contents"]
                        if files is None:
                            print('No file contents.')
                            continue
                        for file in files:  # This also contains the file size....
                            l_ls.append(file['Key'])
                    has_run = True
                except ClientException as e:
                    logger.error(str(e))
                    if i == 4:
                        raise
                    time.sleep(0.4)
        return l_ls

    def path_exists(self, path):
        """
        Return True/False if passed path exists in swift storage.
        """
        conn = self.get_connection()
        result = conn.list_objects(Bucket="Bucket", Prefix=path)
        exists = False
        if 'Contents' in result:
            exists = True
        return exists

    def obj_exists(self, obj_path):
        """
        Return True/False if passed object exists in swift storage.
        """
        return self.path_exists(obj_path)

    def upload_obj(self, swift_path, contents, **kwargs):
        """
        Upload an object (a file contents) into swift storage.
        """
        conn = self.get_connection()
        for i in range(5):
            try:
                conn.put_object(Bucket=self.container_name,
                                Key=swift_path,
                                Body=contents)
            except ClientException as e:
                logger.error(str(e))
                if i == 4:
                    raise
                time.sleep(0.4)
            else:
                break

    def download_obj(self, obj_path, **kwargs):
        """
        Download an object from swift storage.
        """
        conn = self.get_connection()
        for i in range(5):
            try:
                response_object = conn.get_object(Bucket=self.container_name, Key=obj_path)
                obj_contents = response_object['Body'].read()
            except ClientException as e:
                logger.error(str(e))
                if i == 4:
                    raise
                time.sleep(0.4)
            else:
                return obj_contents

    def copy_obj(self, obj_path, dest_path, **kwargs):
        """
        Copy an object to a new destination in swift storage.
        """
        conn = self.get_connection()
        dest = os.path.join('/' + self.container_name, dest_path.lstrip('/'))
        for i in range(5):
            try:
                conn.copy_object(self.container_name, obj_path, dest, **kwargs)
            except ClientException as e:
                logger.error(str(e))
                if i == 4:
                    raise
                time.sleep(0.4)
            else:
                break

    def delete_obj(self, obj_path):
        """
        Delete an object from swift storage.
        """
        conn = self.get_connection()
        for i in range(5):
            try:
                conn.delete_object(self.container_name, obj_path)
            except ClientException as e:
                logger.error(str(e))
                if i == 4:
                    raise
                time.sleep(0.4)
            else:
                break

    def upload_files(self, local_dir, swift_prefix='', **kwargs):
        """
        Upload all the files within a local directory recursively to swift storage.

        By default, the location in swift storage will map 1:1 to the location of
        files in the local filesytem. This location can be remapped by using the
        <swift_prefix>. For example, assume a local directory /home/user/project/data/
        with the following files:

            '/home/user/project/data/file1',
            '/home/user/project/data/dir1/file_d1',
            '/home/user/project/data/dir2/file_d2'

        and we want to upload everything in that directory to object storage, at location
        '/storage'. In this case, swift_prefix='/storage' results in a new list

            '/storage/file1',
            '/storage/dir1/file_d1',
            '/storage/dir2/file_d2'
        """
        # upload all files down the <local_dir>
        conn = self.get_connection()
        s3 = conn.resource('s3')

        for root, dirs, files in os.walk(local_dir):
            swift_base = root.replace(local_dir, swift_prefix, 1) if swift_prefix else root
            for filename in files:
                swift_path = os.path.join(swift_base, filename)
                if not self.obj_exists(swift_path):
                    local_file_path = os.path.join(root, filename)
                    s3.meta.client.upload_file(Filename=swift_path, Bucket=self.container_name)


class StaticStorage(S3Boto3Storage):
    location = settings.AWS_STATIC_LOCATION
    default_acl = 'public-read-write'
