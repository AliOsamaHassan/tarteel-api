from django.contrib.auth.models import User, Group
from rest_framework import serializers
from restapi.models import AnnotatedRecording, DemographicInformation


class DemographicInformationSerializer(serializers.ModelSerializer):
    session_id = serializers.CharField(required=True)

    class Meta:
        model = DemographicInformation
        fields = '__all__'

    def validate_session_id(self, value):
        """Field level validation for session ID string."""
        if value is None or value == '':
            raise serializers.ValidationError("Session ID cannot be null/empty string.")
        return value

    def create(self, validated_data):
        defaults = {'session_id': validated_data.get('session_id', None),
                    'platform': validated_data.get('platform', None),
                    'gender': validated_data.get('gender', None),
                    'qiraah': validated_data.get('qiraah', None),
                    'age': validated_data.get('age', None),
                    'ethnicity': validated_data.get('ethnicity', None)}
        demographic, created = DemographicInformation.objects.update_or_create(
                session_id=validated_data.get('session_id', None),
                defaults=defaults
        )
        print("Demographic created: {}".format(created))
        return demographic


class AnnotatedRecordingSerializer(serializers.ModelSerializer):
    associated_demographic = DemographicInformationSerializer()

    class Meta:
        model = AnnotatedRecording
        fields = '__all__'

    def validate_file(self, value):
        pass


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
