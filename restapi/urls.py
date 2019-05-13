from django.urls import path, re_path

from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('recordings', views.model.AnnotatedRecordingViewSet)
router.register('evaluation_set', views.model.EvaluationViewSet)

urlpatterns = [
    path('demographics/', views.model.DemographicInformationViewList.as_view(),
         name='demographic'),
    path('get_ayah_translit/', views.model.get_ayah_translit),
    path('get_total_count/', views.RecordingsCount.as_view(), name='recordingscount'),
    path('evaluator/', views.model.EvaluationList.as_view()),
    path('submit_evaluation/', views.model.EvaluationSubmission.as_view(),
         name="evaluation_submission"),
    # Site specific info
    path('get_ayah/', views.site.GetAyah.as_view(), name='get_ayah'),
    path('index/', views.site.Index.as_view(), name='api_index'),
    path('about/', views.site.About.as_view(), name='api_about'),
    path('surah/<str:surah_num>/', views.site.GetSurah.as_view(), name='get_surah'),
    re_path(r'^profile/(?P<session_key>[\w-]+)/', views.site.Profile.as_view(),
            name='profile_api'),
    path('download-audio/', views.site.DownloadAudio.as_view()),
]

urlpatterns += router.urls
