from django.urls import path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register('surah', views.SurahViewSet)
router.register('ayah', views.AyahViewSet)
router.register('word', views.AyahWordViewSet)
router.register('translation', views.TranslationViewSet)

urlpatterns = [
    path('get_ayah_translit/', views.get_ayah_translit),
    path('ayah/<int:surah>/<int:ayah>/', views.get_ayah)
]

urlpatterns += router.urls
