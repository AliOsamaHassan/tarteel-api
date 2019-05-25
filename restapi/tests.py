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
    """Test class for the demographics model"""
    def test_post_demographic(self):
        """Test a POST request for the demographic model"""
        url = reverse('demographicinformation-list')
        response = self.client.post(url, demographic_json_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_demographic_no_session(self):
        """Test a POST request for the demographic model with no session ID (required)."""
        url = reverse('demographicinformation-list')
        response = self.client.post(url, demographic_no_session_json_request,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


recording_json_request = {
    'session_id': 'def456',
    'surah_num': 1,
    'ayah_num': 1,
    'hash_string': 'abc123',
    'recitation_mode': 'continuous',
}


class RecordingTestCase(APITestCase):
    """Test class for the annotated recording model."""
    def test_file_upload(self):
        """Test uploading a sample audio file."""
        audio_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'utils', 'test_audio.wav'))
        url = reverse('annotatedrecording-list')
        with open(audio_file_path, 'rb') as audio_file:
            # upload_file = SimpleUploadedFile('recording.wav', data.read(),
            #                                  content_type='audio/x-wav')
            recording_json_request['file'] = audio_file
            response = self.client.post(url, recording_json_request)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
