from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import os

demographic_json_request = {
    "session_id": "arg3prrr1sdb711w85notsd3gaebpc2o",
    "platform": "web",
    "gender": "female",
    "age": "19",
    "ethnicity": "SY",
    "timestamp": "2018-08-06T06:30:46.823000Z",
    "qiraah": None
}

demographic_no_session_json_request = {
    "platform": "web",
    "gender": "female",
    "age": "19",
    "ethnicity": "SY",
    "timestamp": "2018-08-06T06:30:46.823000Z",
    "qiraah": None
}


class DemographicTestCase(APITestCase):
    def test_post_demographic(self):
        url = reverse('demographicinformation-list')
        response = self.client.post(url, demographic_json_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_demographic_no_session(self):
        url = reverse('demographicinformation-list')
        response = self.client.post(url, demographic_no_session_json_request,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# class RecordingTestCase(APITestCase):
#     def test_file_upload(self):
#         audio_file_path = os.path.abspath(
#                 os.path.join(os.path.dirname(__file__), '..', 'utils', 'test_audio.wav'))
#         url = reverse('')