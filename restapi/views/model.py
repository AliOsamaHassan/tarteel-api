# System Imports
from os.path import dirname, abspath
import random
import io
import json
import os
from urllib.request import urlopen
# Django
from django.contrib.auth.models import User, Group
from django_filters import rest_framework as filters
from django.db.models import Count
# Django Rest Framework
from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
# Tarteel Apps
from restapi.serializers import UserSerializer, GroupSerializer, \
    AnnotatedRecordingSerializerPost, AnnotatedRecordingSerializerGet, \
    DemographicInformationSerializer, AnnotatedRecordingSerializer
from restapi.models import AnnotatedRecording, DemographicInformation
from restapi.permissions import RecordingPermissions
from evaluation.models import Evaluation
from evaluation.serializers import EvaluationSerializer
from evaluation.views import get_low_evaluation_count

# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

TOTAL_AYAH_NUM = 6236
BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
INT_NA_VALUE = -1
STRING_NA_VALUE = "N/A"


class AnnotatedRecordingList(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    # permission_classes = (RecordingPermissions,)

    def get(self, request, format=None):
        """Returns the last 10 recordings received."""
        recordings = AnnotatedRecording.objects.all().order_by('-timestamp')[:10]
        serializer = AnnotatedRecordingSerializerGet(recordings, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Creates a recording record in the DB using a serializer. Attempts
            to link a demographic if a session key exists.
        """

        # User tracking - Ensure there is always a session key.
        session_key = request.session.session_key

        if hasattr(request.data, "session_id"):
            session_key = request.data["session_id"]
        elif not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Check if demographic with key exists (default to None)
        # TODO(piraka9011): Associate with user login once auth is developed.
        request.data['associated_demographic'] = None
        demographic = DemographicInformation.objects.filter(session_id=session_key).order_by('-timestamp')
        if demographic.exists():
            request.data['associated_demographic'] = demographic[0].id
        new_recording = AnnotatedRecordingSerializerPost(data=request.data)
        print("Received recording data: {}".format(new_recording))
        if new_recording.is_valid(raise_exception=True):
            new_recording.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response("Invalid data, check the post request for all necessary data.",
                        status=status.HTTP_400_BAD_REQUEST)


class AnnotatedRecordingFilter(filters.FilterSet):
    surah = filters.NumberFilter(field_name='surah_num')
    ayah = filters.NumberFilter(field_name='ayah_num')
    gender = filters.CharFilter(field_name='associated_demographic__gender')

    class Meta:
        model = AnnotatedRecording
        fields = ['gender', 'surah', 'ayah']


class AnnotatedRecordingViewSet(viewsets.ModelViewSet):
    """API to handle query parameters
    Example: api/v1/recordings/?surah=114&ayah=1
    """
    serializer_class = AnnotatedRecordingSerializer
    queryset = AnnotatedRecording.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AnnotatedRecordingFilter
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class DemographicInformationViewList(APIView):
    """API endpoint that allows demographic information to be viewed or edited.
    """

    def get(self, request, format=None):
        recordings = DemographicInformation.objects.all().order_by('-timestamp')
        serializer = DemographicInformationSerializer(recordings, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # User tracking - Ensure there is always a session key.
        session_key = request.session.session_key

        if hasattr(request.data, "session_id"):
            session_key = request.data["session_id"]
        elif not session_key:
            return Response(
                "Can't submit demographic data for a user that doesn't exist.",
                status=status.HTTP_400_BAD_REQUEST)

        request.data['session_id'] = session_key

        new_demographic = DemographicInformationSerializer(data=request.data)
        print("Received demographic data: {}".format(request.data))
        if new_demographic.is_valid(raise_exception=True):
            new_demographic.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response("Invalid data, check the post request for all necessary data.",
                        status=status.HTTP_400_BAD_REQUEST)


class EvaluationFilter(filters.FilterSet):
    EVAL_CHOICES = (
    ('correct', 'Correct'),
    ('incorrect', 'Incorrect'))

    surah = filters.NumberFilter(field_name='associated_recording__surah_num')
    ayah = filters.NumberFilter(field_name='associated_recording__ayah_num')
    evaluation = filters.ChoiceFilter(choices=EVAL_CHOICES)
    associated_recording = filters.ModelChoiceFilter(queryset=AnnotatedRecording.objects.all())

    class Meta:
        model = Evaluation
        fields = ['surah', 'ayah', 'evaluation', 'associated_recording']


class EvaluationViewSet(viewsets.ModelViewSet):
    """API to handle query parameters
    Example: api/v1/evaluations/?surah=114&ayah=1&evaluation=correct
    """
    serializer_class = EvaluationSerializer
    queryset = Evaluation.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class=EvaluationFilter


class EvaluationList(APIView):
    def get(self, request, *args, **kwargs):
        random_recording = get_low_evaluation_count()
        # Load the Arabic Quran from JSON
        URL = 'https://uc520b745555b7bcf9da297533da.dl.dropboxusercontent.com/cd/0/get/' \
              'Ac4fYqiJ-3hSJn4gp2_jyb9dlZhwJ2uJH3NG0SpImV26CQoGjFwaJ0umMXxjxInOdnHAWtCz' \
              'DabpG--i50qu6VYSUstHSStzflEXgACwEYwDiNysbQX078k6ZUez4n4WZz0/file?dl=1'
        data = urlopen(URL)
        data_str = ''
        for line in data:
            data_str += line.decode('utf-8')
        quran = json.loads(data)

        # Fields
        surah_num = str(random_recording.surah_num)
        ayah_num = random_recording.ayah_num
        audio_url = random_recording.file.url
        ayah = quran[surah_num]["verses"][ayah_num - 1]
        recording_id = random_recording.id

        ayah["audio_url"] = audio_url
        ayah["recording_id"] = recording_id

        return Response(ayah)

    def post(self, request, *args, **kwargs):
        if "recording_id" in request.data:
            recording_id = request.data['recording_id']
            recording = list(AnnotatedRecording.objects.filter(id=recording_id).values())[0]
        else:
            ayah_num = int(request.data['ayah'])
            surah_num = str(request.data['surah'])
            # This is the code of get_low_evaluation_count() but this is getting the
            # choices of a specific ayah
            recording_evals = AnnotatedRecording.objects.filter(surah_num=surah_num,
                                                                ayah_num=ayah_num).annotate(total=Count('evaluation'))
            recording_evals_dict = {entry: entry.total for entry in recording_evals}

            min_evals = min(recording_evals_dict.values())
            min_evals_recordings = [k for k, v in recording_evals_dict.items() if v == min_evals]

            recording = {random.choice(min_evals_recordings)}

        # Load the Arabic Quran from JSON
        URL = 'https://uc520b745555b7bcf9da297533da.dl.dropboxusercontent.com/cd/0/get/' \
              'Ac4fYqiJ-3hSJn4gp2_jyb9dlZhwJ2uJH3NG0SpImV26CQoGjFwaJ0umMXxjxInOdnHAWtCz' \
              'DabpG--i50qu6VYSUstHSStzflEXgACwEYwDiNysbQX078k6ZUez4n4WZz0/file?dl=1'
        data = urlopen(URL)
        data_str = ''
        for line in data:
            data_str += line.decode('utf-8')
        quran = json.loads(data)

        ayah = quran[surah_num]["verses"][ayah_num - 1]

        if hasattr(recording, "file"):
            ayah["audio_url"] = recording.file.url
        ayah["recording_id"] = recording.id

        return Response(ayah)


class EvaluationSubmission(APIView):
    def post(self, request, *args, **kwargs):
        # User tracking - Ensure there is always a session key.
        session_key = request.session.session_key

        if hasattr(request.data, "session_id"):
            session_key = request.data["session_id"]
        elif not session_key:
            request.session.create()
            session_key = request.session.session_key

        ayah = request.data['ayah']
        data = {
            "session_id": session_key,
            "associated_recording": ayah["recording_id"],
            "evaluation": ayah["evaluation"]
        }
        new_evaluation = EvaluationSerializer(data=data)
        try:
            new_evaluation.is_valid(raise_exception=True)
            new_evaluation.save()
        except serializers.ValidationError:
            return Response("Invalid serializer data.",
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


