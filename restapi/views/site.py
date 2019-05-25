# System Imports
from collections import defaultdict
import datetime
import json
import os
import random
from urllib.request import urlopen
# Django
from django.db.models import Count
# Django Rest Framework
from rest_framework.views import APIView
from rest_framework.response import Response
# Tarteel Apps
from .utils import _sort_recitations_dict_into_lists
from restapi.models import AnnotatedRecording, DemographicInformation
from evaluation.models import Evaluation

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOTAL_AYAH_NUM = 6236


class About(APIView):
    """ Gets the required data for About page Includes queries for graphs."""

    def get(self, request):
        """ Gets the required data for About page Includes queries for graphs.

        :param request: rest API request object.
        :type request: Request
        :return: HttpResponse with total number of recordings and labels for graphs
        :rtype: HttpResponse
        """

        # User tracking - Ensure there is always a session key.
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Number of recordings
        recording_count = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False).count()
        user_recording_count = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False, session_id=session_key).count()
        unique_user_count = DemographicInformation.objects.count()

        # Demographic data for the graphs.
        # Gender
        gender_labels = ['male', 'female']
        gender_counts = DemographicInformation.objects.filter(
            gender__in=gender_labels).values('gender').annotate(
            the_count=Count('gender'))
        gender_labels = [k['gender'] for k in gender_counts]
        gender_data = [k['the_count'] for k in gender_counts]

        # Age
        age_labels = ['13', '19', '26', '36', '46', '56']
        age_counts = DemographicInformation.objects.filter(
            age__in=age_labels).values('age').annotate(
            the_count=Count('age'))
        age_labels = [k['age'] for k in age_counts]
        age_label_map = {'13': '13-18',
                         '19': '19-25',
                         '26': '26-35',
                         '36': '36-45',
                         '46': '46-55',
                         '56': '56+'}
        age_labels = [age_label_map[a] for a in age_labels]
        age_data = [k['the_count'] for k in age_counts]

        # Ethnicity
        ethnicity_counts = DemographicInformation.objects.values(
            'ethnicity').annotate(the_count=Count('ethnicity')).order_by(
            '-the_count')[:6]
        ethnicity_labels = [k['ethnicity'] for k in ethnicity_counts]
        ethnicity_data = [k['the_count'] for k in ethnicity_counts]

        # Get ayah data for the graphs.
        ayah_counts = list(AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False).values(
            'surah_num', 'ayah_num').annotate(count=Count('pk')))
        raw_counts = [ayah['count'] for ayah in ayah_counts]

        # Auto increment the labels based on the number of ayahs we have
        min_count_limit = 50    # Minimum number of recordings to qualify for a label
        label_limit = 20        # Max label number
        max_label_count = 5     # Max number of labels
        curr_label_count = 0    # How many labels we have so far
        count_labels = []       # Store our labels
        count_data = []         # Store the value for each label
        for i in range(0, label_limit):
            if curr_label_count >= max_label_count:
                break   # Finished
            if raw_counts.count(i) > min_count_limit:
                curr_label_count += 1
                count_labels.append(str(i))
                count_data.append(raw_counts.count(i))
        count_labels.append("{}+".format(str(i)))
        count_data.append(TOTAL_AYAH_NUM - sum(count_data))

        # Add commas to this number as it is used for display.
        recording_count_formatted = "{:,}".format(recording_count)

        return Response({
            'recording_count': recording_count,
            'recording_count_formatted': recording_count_formatted,
            'gender_labels': gender_labels,
            'gender_data': gender_data,
            'unique_user_count': unique_user_count,
            'user_recording_count': user_recording_count,
            'age_labels': age_labels,
            'age_data': age_data,
            'count_labels': count_labels,
            'count_data': count_data,
            'session_id': session_key,
            'ethnicity_labels': ethnicity_labels,
            'ethnicity_data': ethnicity_data
        })


class DownloadAudio(APIView):
    def get(self, request, *args, **kwargs):
        """Returns the URLs of 15 random, non-empty audio samples.

         :param request: rest API request object.
         :type request: Request
         :return: Response with list of file urls.
         :rtype: HttpResponse
         """
        files = AnnotatedRecording.objects.filter(file__gt='',
                                                  file__isnull=False).order_by('timestamp')[5000:6000]
        random.seed(0)  # ensures consistency in the files displayed.
        rand_files = random.sample(list(files), 15)
        file_urls = [f.file.url for f in rand_files]

        return Response(file_urls)


class GetSurah(APIView):
    """Gets all the ayahs in specific surah given by num"""

    def get(self, request, surah_num, format=None):
        """Returns the ayahs of specific surah.

        :param request: rest API request object.
        :type request: Request
        :return: A JSON response with the requested text.
        :rtype: JsonResponse
        """
        # Load the Uthmani Quran from JSON
        quran_data_url = 'https://s3.amazonaws.com/zappa-tarteel-static/data.json'
        data_response = urlopen(quran_data_url)
        json_data = data_response.read()
        json_str = json_data.decode('utf-8-sig')
        quran = json.loads(json_str)

        ayah_list = quran[surah_num]

        res = {
            'chapter_id': surah_num,
            'ayahs': ayah_list,
        }

        return Response(res)


class Index(APIView):

    def get(self, request, format=None):
        """ Gets today's and total recording counts as well as checks
        for whether we have demographic info for the session.

        :param request: rest API request object.
        :type request: Request
        :return: HttpResponse with total number of recordings, today's recordings, and a
        check to ask for demographic info.
        :rtype: HttpResponse
        """

        # User tracking - Ensure there is always a session key.
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        recording_count = AnnotatedRecording.objects.filter(
            file__gt='', file__isnull=False).count()
        evaluations = Evaluation.objects.all().count()
        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        # Check if we need demographics for this session
        ask_for_demographics = DemographicInformation.objects.filter(
                session_id=session_key).exists()

        daily_count = AnnotatedRecording.objects.filter(
            file__gt='', timestamp__gt=yesterday).exclude(file__isnull=True).count()
        return Response({
            'recording_count': recording_count,
            'daily_count': daily_count,
            'evaluations_count': evaluations,
            'session_id': session_key,
            'ask_for_demographics': ask_for_demographics
        })


class Profile(APIView):

    def get(self, request, session_key):
        """ Returns the session profile data.

         :param request: rest API request object.
         :type request: Request
         :param session_key: string representing the session key for the user
         :type session_key: str
         :return: Just another django mambo.
         :rtype: HttpResponse
         """

        # User tracking - Ensure there is always a session key.
        # This may be different from the one provided in the URL.
        my_session_key = request.session.session_key
        if not my_session_key:
            request.session.create()
            my_session_key = request.session.session_key

        last_week = datetime.date.today() - datetime.timedelta(days=7)

        # Get the weekly counts.
        last_weeks = [
            datetime.date.today() - datetime.timedelta(days=days)
            for days in [6, 13, 20, 27, 34]
        ]
        dates = []
        weekly_counts = []
        for week in last_weeks:
            dates.append(week.strftime('%m/%d/%Y'))
            count = AnnotatedRecording.objects.filter(
                file__gt='', file__isnull=False, session_id=session_key,
                timestamp__gt=week, timestamp__lt=week + datetime.timedelta(
                            days=7)).count()
            weekly_counts.append(count)

        recording_count = AnnotatedRecording.objects.filter(
                file__gt='', file__isnull=False).count()

        # Construct dictionaries of the user's recordings.
        user_recording_count = AnnotatedRecording.objects.filter(
                file__gt='', file__isnull=False, session_id=session_key).count()
        recent_recordings = AnnotatedRecording.objects.filter(
                file__gt='', file__isnull=False, session_id=session_key,
                timestamp__gt=last_week)
        recent_dict = defaultdict(list)
        [recent_dict[rec.surah_num].append(
                (rec.ayah_num, rec.file.url)) for rec in recent_recordings
        ]
        old_recordings = AnnotatedRecording.objects.filter(
                file__gt='', file__isnull=False, session_id=session_key,
                timestamp__lt=last_week)
        old_dict = defaultdict(list)
        [old_dict[rec.surah_num].append(
                (rec.ayah_num, rec.file.url)) for rec in old_recordings
        ]

        recent_lists = _sort_recitations_dict_into_lists(recent_dict)
        old_lists = _sort_recitations_dict_into_lists(old_dict)

        return Response({
            'session_id': my_session_key,
            'recent_dict': dict(recent_dict),
            'recent_lists': recent_lists,
            'old_lists': old_lists,
            'dates': dates[::-1],
            'weekly_counts': weekly_counts[::-1],
            'old_dict': dict(old_dict),
            'recording_count': recording_count,
            'user_recording_count': user_recording_count
        })
