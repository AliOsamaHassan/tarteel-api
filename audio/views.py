# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import random
import requests
from os.path import join, dirname, abspath
from django.db.models import Count
from django.http import JsonResponse
from restapi.models import AnnotatedRecording
from rest_framework.decorators import api_view
from ranged_fileresponse import RangedFileResponse
from urllib.request import urlopen


# =============================================== #
#           Constant Global Definitions           #
# =============================================== #

TOTAL_AYAH_NUM = 6236
BASE_DIR = dirname(dirname(abspath(__file__)))
INT_NA_VALUE = -1
STRING_NA_VALUE = "N/A"

# ===================================== #
#           Utility Functions           #
# ===================================== #


def get_low_ayah_count(quran_dict, line_length):
    """Finds the ayah under the line length with the lowest number of recordings

    :param quran_dict: The uthmani or transliteration quran loaded from a json
    as a dictionary.
    :type quran_dict: dict
    :param line_length: The maximum number of characters an ayah should have.
    :type line_length: int
    :returns: The surah number, ayah number, and text of the ayah as a tuple.
    :rtype: tuple(int, int, string)
    """
    ayah_counts = list(AnnotatedRecording.objects.filter(
        file__gt='', file__isnull=False).values(
        'surah_num', 'ayah_num').annotate(count=Count('pk')))
    ayah_count_dict = {(entry['surah_num'], entry['ayah_num']): entry['count'] for entry in ayah_counts}

    min_count = float("inf")
    surah_list = quran_dict['surahs']
    ayah_data_list = []
    for surah in surah_list:
        surah_num = int(surah['num'])
        for ayah in surah['ayahs']:
            ayah_num = int(ayah['num'])
            ayah_length = len(ayah['text'])
            if ayah_length < line_length:
                if (surah_num, ayah_num) in ayah_count_dict:  # if it's the shortest ayah, return its information
                    if ayah_count_dict[(surah_num, ayah_num)] < min_count:
                        ayah_data = surah_num, ayah_num, ayah['text']
                        ayah_data_list = [ayah_data]
                        min_count = ayah_count_dict[(surah_num, ayah_num)]
                    elif ayah_count_dict[(surah_num, ayah_num)] == min_count:
                        ayah_data = surah_num, ayah_num, ayah['text']
                        ayah_data_list.append(ayah_data)
                else:  # if we have no recordings of this ayah, it automatically takes precedence
                    ayah_data = surah_num, ayah_num, ayah['text']
                    if min_count == 0:
                        ayah_data_list.append(ayah_data)
                    else:
                        ayah_data_list.append(ayah_data)
                        min_count = 0
    return random.choice(ayah_data_list)


def _sort_recitations_dict_into_lists(dictionary):
    """ Helper method that simply converts a dictionary into two lists sorted
    correctly.

    :param dictionary: Dict of two lists
    :type dictionary: dict
    :return Sorted dict
    :rtype dict
    """
    if not dictionary:
        return zip([], [])
    surah_nums, ayah_lists = zip(*dictionary.items())
    surah_nums, ayah_lists = list(surah_nums), list(ayah_lists)
    surah_nums, ayah_tuples = zip(*sorted(
        zip(surah_nums, ayah_lists)))  # Now they are sorted according to surah_nums
    for i in range(len(ayah_lists)):
        ayah_lists[i] = sorted(list(ayah_tuples[i]))
    return zip(surah_nums, ayah_lists)


# ================================= #
#           API Functions           #
# ================================= #


@api_view(['GET'])
def get_ayah_translit(request):
    """Returns the transliteration text of an ayah.
    Request body should have a JSON with "surah" (int) and "ayah" (int).

    :param request: rest API request object.
    :type request: Request
    :return: A JSON response with the requested text.
    :rtype: JsonResponse
    """
    # Load the Transliteration Quran from JSON
    translit_data_url = 'https://s3.amazonaws.com/zappa-tarteel-static/data-translit.json'
    data_response = urlopen(translit_data_url)
    json_data = data_response.read()
    json_str = json_data.decode('utf-8-sig')
    quran_translit = json.loads(json_str)
    quran_translit = quran_translit['quran']

    surah = int(request.data['surah'])
    ayah = int(request.data['ayah'])

    # The parameters `surah` and `ayah` are 1-indexed, so subtract 1.
    line = quran_translit["surahs"][surah - 1]["ayahs"][ayah - 1]["text"]

    # Format as json and return response
    result = {"line": line}

    return JsonResponse(result)


# ===================================== #
#           Static Page Views           #
# ===================================== #

def stream_audio_url(request, url):
    file = requests.get(url, allow_redirects=True)
    response = RangedFileResponse(request, file.content, content_type='audio/wav')
    response['Content-Disposition'] = 'attachment; filename="evaluation.wav"'
    return response
