import logging
import json
import io
from unittest import mock

from django.test import TestCase, tag
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status

from uploadedfiles.s3_storage import PublicMediaStorage
from uploadedfiles.models import UploadedFile, uploaded_file_path
from uploadedfiles import views


# To run a test from the command line:
#    python manage.py test uploadedfiles.tests.test_storage.PublicMediaStorageTests.test_ls
class PublicMediaStorageTests(TestCase):
    """
    Test the Public Media Storage
    """

    def setUp(self):
        # avoid cluttered console output (for instance logging all the http requests)
        logging.disable(logging.WARNING)

        self.content_type = 'application/vnd.collection+json'
        self.chris_username = 'chris'
        self.chris_password = 'chrispass'
        self.username = 'test'
        self.password = 'testpass'
        self.other_username = 'boo'
        self.other_password = 'far'

        # create the chris superuser and two additional users
        User.objects.create_user(username=self.chris_username,
                                 password=self.chris_password)
        User.objects.create_user(username=self.other_username,
                                 password=self.other_password)
        user = User.objects.create_user(username=self.username,
                                        password=self.password)

        # create a file in the DB "already uploaded" to the server)
        self.s3_manager = PublicMediaStorage()

    def tearDown(self):
        # re-enable logging
        logging.disable(logging.NOTSET)

    def test_ls(self):
        results = self.s3_manager.ls('chris/uploads')
        for result in results:
            print(result);

    def test_download_object(self):
        results = self.s3_manager.download_obj('chris/uploads/test_file1')
        print(results)

    def test_upload_object(self):
        self.s3_manager.upload_obj('chris/uploads/test_file1', "test file1 contents")

