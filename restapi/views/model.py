# System Imports
from os.path import dirname, abspath
# Django
from django_filters import rest_framework as filters
# Django Rest Framework
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
# Tarteel Apps
from restapi.serializers import DemographicInformationSerializer, \
    AnnotatedRecordingSerializer
from restapi.models import AnnotatedRecording, DemographicInformation
from restapi.permissions import RecordingPermissions


# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

TOTAL_AYAH_NUM = 6236
BASE_DIR = dirname(dirname(dirname(abspath(__file__))))
INT_NA_VALUE = -1
STRING_NA_VALUE = "N/A"


class AnnotatedRecordingFilter(filters.FilterSet):
    surah = filters.NumberFilter(field_name='surah_num')
    ayah = filters.NumberFilter(field_name='ayah_num')
    gender = filters.CharFilter(field_name='associated_demographic__gender')

    class Meta:
        model = AnnotatedRecording
        fields = ['gender', 'surah', 'ayah']


class AnnotatedRecordingViewSet(viewsets.ModelViewSet):
    """View set to handle query parameters and all request types
    Example: v1/recordings/?surah=114&ayah=1
    """
    serializer_class = AnnotatedRecordingSerializer
    queryset = AnnotatedRecording.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AnnotatedRecordingFilter
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()

        has_file = self.request.query_params.get('has_file', None)
        if has_file is not None:
            queryset = queryset.filter(file__gt='', file__isnull=False)

        return queryset

    @action(detail=False, methods=['get'])
    def get_total_count(self, request):
        recording_count = AnnotatedRecording.objects.filter(file__gt='',
                                                            file__isnull=False).count()
        response = {'count': recording_count}
        return Response(response)


class DemographicFilter(filters.FilterSet):
    gender = filters.CharFilter(field_name='gender')
    qiraah = filters.CharFilter(field_name='qiraah')
    age = filters.CharFilter(field_name='age')
    ethnicity = filters.CharFilter(field_name='ethnicity')

    class Meta:
        model = DemographicInformation
        fields = ['gender', 'qiraah', 'age', 'ethnicity']


class DemographicViewSet(viewsets.ModelViewSet):
    """View set for demographics."""
    serializer_class = DemographicInformationSerializer
    queryset = DemographicInformation.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = DemographicFilter

