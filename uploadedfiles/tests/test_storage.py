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


class PublicMediaStorageTestsUpload(TestCase):
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

    def test_upload_object(self):
        reponse = self.s3_manager.upload_obj('chris/uploads/test_file1', "test file1 contents")
        status = reponse['ResponseMetadata']['HTTPStatusCode']
        self.assertEqual(status, 200,
                         f"Status code: {status}")

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

        self.s3_manager.upload_obj('chris/uploads/test_file1', "test file1 contents")

    def tearDown(self):
        # re-enable logging
        logging.disable(logging.NOTSET)

    # def test_upload_object(self):
    #     reponse = self.s3_manager.upload_obj('chris/uploads/test_file1', "test file1 contents")
    #     self.assertEqual(reponse['ResponseMetadata']['HTTPStatusCode'], 200)
    #     print("uploaded")
        
    def test_ls(self):
        results = self.s3_manager.ls('chris/uploads')
        # for result in results:
        #     print(result);
        self.assertTrue(
            any('chris/uploads/test_file1' in result for result in results),
            print((f"ls did not return target, it returned: "
                    f"{[result for result in results]}")))

    def test_path_exists(self):
        self.assertTrue(self.s3_manager.path_exists('chris/uploads'),
                       'THE PATH "chris/uploads" does not exist')

    def test_object_exists(self):
        self.assertTrue(self.s3_manager.obj_exists('chris/uploads/test_file1'),
                        'THE OBJECT "chris/uploads/test_file1" does not exist')

    def test_download_object(self):
        results = self.s3_manager.download_obj('chris/uploads/test_file1')
        self.assertTrue(b'test file1 contents' in results,
                        f'File contents not as expected: {results}')

    def test_delete_object(self):
        results = self.s3_manager.delete_obj('chris/uploads/test_file1')
        self.assertFalse(self.s3_manager.obj_exists('chris/uploads/test_file1'),
                         "object still exists")