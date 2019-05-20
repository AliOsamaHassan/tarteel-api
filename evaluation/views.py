# -*- coding: utf-8 -*-
# Django
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.forms.models import model_to_dict
from django_filters import rest_framework as filters
# REST
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
# Tarteel
from evaluation.models import TajweedEvaluation, Evaluation
from evaluation.serializers import TajweedEvaluationSerializer, EvaluationSerializer
from restapi.models import AnnotatedRecording
from quran.models import Ayah
# Python
import io
import json
import os
import random

# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===================================== #
#           Utility Functions           #
# ===================================== #


def get_tajweed_rule(surah_num=0, ayah_num=0, random_rule=False):
    """If random_rule is true then we get a random tajweed rule. Otherwise returns a
    specific rule. Both options return the text and word index.
    :return: A tuple with the surah & ayah number, text, rule, and word position
    :rtype: tuple(int, int, str, str, int) or tuple(str, str, int)
    """
    TAJWEED_FILE = os.path.join(BASE_DIR, 'utils/data-rules.json')
    with io.open(TAJWEED_FILE) as file:
        tajweed_rules = json.load(file)
        tajweed_rules = tajweed_rules['quran']
        file.close()

    UTHMANI_FILE = os.path.join(BASE_DIR, 'utils/data-uthmani.json')
    with io.open(UTHMANI_FILE, 'r', encoding="utf-8-sig") as file:
        uthmani_q = json.load(file)
        uthmani_q = uthmani_q['quran']
        file.close()

    if random_rule:
        random_surah = random.choice(tajweed_rules['surahs'])
        surah_num = random_surah['num']
        random_ayah = random.choice(random_surah['ayahs'])
        ayah_num = random_ayah['num']
        rule_dict = random.choice(random_ayah['rules'])
    else:
        rule_dict = tajweed_rules['surah'][surah_num - 1]['ayahs'][ayah_num - 1]
    rule = rule_dict['rule']
    rule_start = rule_dict['start']
    rule_end = rule_dict['end']

    # 1-indexed
    ayah_text = uthmani_q['surahs'][surah_num - 1]['ayahs'][ayah_num - 1]['text']
    ayah_text_list = ayah_text.split(" ")
    # Get the index of the word we're looking for
    position = 0
    curr_word_ind = 0
    for i, word in enumerate(ayah_text_list):
        position += len(word)
        if position >= rule_start:
            curr_word_ind = i
            break

    if random_rule:
        return surah_num, ayah_num, ayah_text, rule, curr_word_ind

    return ayah_text, rule, curr_word_ind


def is_evaluator(user):
    if user:
        return user.groups.filter(name='evaluator').exists()
    return False


def get_low_evaluation_count():
    """Finds a recording with the lowest number of evaluations
    :returns: A random AnnotatedRecording object which has the minimum evaluations
    :rtype: AnnotatedRecording
    """

    recording_evals = AnnotatedRecording.objects.annotate(total=Count('evaluation'))
    recording_evals_dict = {entry : entry.total for entry in recording_evals}

    min_evals = min(recording_evals_dict.values())
    min_evals_recordings = [k for k, v in recording_evals_dict.items() if v==min_evals]

    return random.choice(min_evals_recordings)

# ================================= #
#           API Functions           #
# ================================= #


class EvaluationFilter(filters.FilterSet):
    EVAL_CHOICES = (
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')
    )

    surah = filters.NumberFilter(field_name='associated_recording__surah_num')
    ayah = filters.NumberFilter(field_name='associated_recording__ayah_num')
    evaluation = filters.ChoiceFilter(choices=EVAL_CHOICES)
    associated_recording = filters.ModelChoiceFilter(
            queryset=AnnotatedRecording.objects.all()
    )

    class Meta:
        model = Evaluation
        fields = ['surah', 'ayah', 'evaluation', 'associated_recording']


class EvaluationViewSet(viewsets.ModelViewSet):
    """API to handle query parameters
    Example: v1/evaluations/?surah=114&ayah=1&evaluation=correct
    """
    serializer_class = EvaluationSerializer
    queryset = Evaluation.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = EvaluationFilter


class EvaluationList(APIView):
    def get(self, request, *args, **kwargs):
        random_recording = get_low_evaluation_count()

        # Fields
        surah_num = random_recording.surah_num
        ayah_num = random_recording.ayah_num
        audio_url = random_recording.file.url
        ayah = Ayah.objects.get(surah__number=surah_num, number=ayah_num)
        ayah = model_to_dict(ayah)
        recording_id = random_recording.id

        ayah["audio_url"] = audio_url
        ayah["recording_id"] = recording_id

        return Response(ayah)

    def post(self, request, *args, **kwargs):
        print("POST evaluator/:\n{}".format(request.data))
        ayah_num = int(request.data['ayah'])
        surah_num = str(request.data['surah'])

        if "recording_id" in request.data:
            recording_id = request.data['recording_id']
            recording = AnnotatedRecording.objects.get(id=recording_id)
        else:
            # This is the code of get_low_evaluation_count() but this is getting the
            # choices of a specific ayah
            recording_evals = AnnotatedRecording.objects.filter(
                    surah_num=surah_num, ayah_num=ayah_num).annotate(
                    total=Count('evaluation')
            )
            recording_evals_dict = {entry: entry.total for entry in recording_evals}

            min_evals = min(recording_evals_dict.values())
            min_evals_recordings = [
                k for k, v in recording_evals_dict.items() if v == min_evals
            ]

            recording = {random.choice(min_evals_recordings)}

        # Load the Arabic Quran from JSON
        ayah = Ayah.objects.get(surah__number=surah_num, number=ayah_num)
        ayah = model_to_dict(ayah)

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


class TajweedEvaluationList(APIView):
    """API Endpoint that allows tajweed evaluations to be posted or
    retrieved """

    def get(self, request, format=None):
        evaluations = TajweedEvaluation.objects.all().order_by('-timestamp')
        tajweed_serializer = TajweedEvaluationSerializer(evaluations, many=True)
        return Response(tajweed_serializer.data)

    def post(self, request, *args, **kwargs):
        print("EVALUATOR: Received a tajweed evaluation:\n{}".format(request.data))
        new_evaluation = TajweedEvaluationSerializer(data=request.data)
        if new_evaluation.is_valid(raise_exception=True):
            new_evaluation.save()
            return Response(new_evaluation.data, status=status.HTTP_201_CREATED)
        return Response(new_evaluation.errors, status=status.HTTP_400_BAD_REQUEST)

# ===================================== #
#           Static Page Views           #
# ===================================== #


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def get_evaluations_count(request, format=None):
    evaluations = Evaluation.objects.all().count()
    res = {
        "count": evaluations
    }
    return Response(res)


@login_required
@user_passes_test(is_evaluator, login_url='/')
def tajweed_evaluator(request):
    """Returns a random ayah for an expert to evaluate for any mistakes.

    :param request: rest API request object.
    :type request: Request
    :return: Rendered view of evaluator page with form, ayah info, and URL.
    :rtype: HttpResponse
    """
    # User tracking - Ensure there is always a session key.
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # Get a random tajweed rule and make sure we have something to display
    recordings = None
    while not recordings:
        surah_num, ayah_num, ayah_text, rule, word_index = get_tajweed_rule(random_rule=True)
        recordings = AnnotatedRecording.objects.filter(file__gt='', file__isnull=False,
                                                       surah_num=surah_num,
                                                       ayah_num=ayah_num)
    random_recording = random.choice(recordings)

    # Make sure we avoid negative count
    prev_word_ind = word_index - 1 if word_index > 0 else None
    # Make sure we avoid overflow
    ayah_text_list = ayah_text.split(" ")
    next_word_ind = word_index + 1 if word_index + 1 < len(ayah_text_list) else None
    # Fields
    audio_url = random_recording.file.url
    recording_id = random_recording.id

    # Get text rep of rule
    category_dict = dict(TajweedEvaluation.CATEGORY_CHOICES)
    rule_text = category_dict[rule]

    return render(request, 'evaluation/tajweed_evaluator.html',
                  {'session_key': session_key,
                   'rule_text': rule_text,
                   'rule_id': rule,
                   'surah_num': surah_num,
                   'ayah_num': ayah_num,
                   'ayah_text': ayah_text_list,
                   'word_index': word_index,
                   'prev_word_index': prev_word_ind,
                   'next_word_index': next_word_ind,
                   'audio_url': audio_url,
                   'recording_id': recording_id})

