import random
# Django
from django_filters import rest_framework as filters
from django.forms.models import model_to_dict
# Django Rest Framework
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
# Quran app
from quran.models import Surah, Ayah, AyahWord, Translation
import quran.serializers


class SurahFilter(filters.FilterSet):
    """Filter surahs by name, number or ayah number."""
    ayah = filters.NumberFilter(field_name='ayah__number')
    surah = filters.NumberFilter(field_name='number')
    name = filters.NumberFilter(field_name='name')

    class Meta:
        model = Surah
        fields = ['ayah', 'surah', 'name']


class SurahViewSet(viewsets.ReadOnlyModelViewSet):
    """Read only view set for surahs."""
    queryset = Surah.objects.all()
    serializer_class = quran.serializers.SurahSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SurahFilter


class AyahFilter(filters.FilterSet):
    """Filter ayahs by sajdahs, surah or ayah numbers."""
    surah = filters.NumberFilter(field_name='surah__number')
    ayah = filters.NumberFilter(field_name='number')
    sajdah = filters.BooleanFilter(field_name='sajdah')

    class Meta:
        model = Ayah
        fields = ['surah', 'ayah', 'sajdah']


class AyahViewSet(viewsets.ReadOnlyModelViewSet):
    """Read only view set for ayahs."""
    queryset = Ayah.objects.all()
    serializer_class = quran.serializers.AyahSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AyahFilter

    @action(detail=False, methods=['get'])
    def random(self, request):
        # User tracking - Ensure there is always a session key.
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        ayah_count = Ayah.objects.count() - 1
        rand_index = random.randint(0, ayah_count)
        rand_ayah = Ayah.objects.all()[rand_index]
        surah_num = rand_ayah.surah.number
        ayah_num = rand_ayah.number
        words = AyahWord.objects.filter(ayah=rand_ayah, ayah__number=ayah_num,
                                        ayah__surah__number=surah_num)
        ayah_dict = model_to_dict(rand_ayah)
        ayah_dict['words'] = list(reversed(words.values()))
        ayah_dict['session_id'] = session_key

        return Response(ayah_dict)


class AyahWordFilter(filters.FilterSet):
    """Filter words by surah, ayah, and word number."""
    surah = filters.NumberFilter(field_name='ayah__surah__number')
    ayah = filters.NumberFilter(field_name='ayah__number')
    number = filters.NumberFilter(field_name='number')

    class Meta:
        model = AyahWord
        fields = ['surah', 'ayah', 'number']


class AyahWordViewSet(viewsets.ReadOnlyModelViewSet):
    """Read only view set for an ayah's words."""
    queryset = AyahWord.objects.all()
    serializer_class = quran.serializers.AyahWordSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AyahWordFilter


class TranslationFilter(filters.FilterSet):
    """Filter translations by surah or ayah number or translation type and language."""
    surah = filters.NumberFilter(field_name='ayah__surah__number')
    ayah = filters.NumberFilter(field_name='ayah__number')
    translation = filters.CharFilter(field_name='translation_type')
    language = filters.CharFilter(field_name='language')

    class Meta:
        model = Translation
        fields = ['surah', 'ayah', 'translation', 'language']


class TranslationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read only view set for an ayah's translation."""
    queryset = Translation.objects.all()
    serializer_class = quran.serializers.Translation
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AyahWordFilter


@api_view(['GET'])
def get_surah(request, surah_num):
    """Returns the ayahs of specific surah.

    :param request: rest API request object.
    :type request: Request
    :return: A JSON response with the requested text.
    :rtype: JsonResponse
    """
    ayahs = Ayah.objects.filter(surah__number=int(surah_num))
    response = {
        'ayahs': ayahs
    }
    return Response(response)


@api_view(['GET'])
def get_ayah_translit(request):
    """Returns the transliteration text of an ayah.
    Request body should have a JSON with "surah" (int) and "ayah" (int).

    :param request: rest API request object.
    :type request: Request
    :return: A JSON response with the requested text.
    :rtype: JsonResponse
    """
    surah = int(request.data['surah'])
    ayah = int(request.data['ayah'])
    line = Translation.objects.get(ayah__surah__number=surah, ayah__number=ayah).text
    # Format as JSON and return response
    result = {"line": line}
    return Response(result)
