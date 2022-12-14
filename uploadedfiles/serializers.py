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
