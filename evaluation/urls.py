from django.urls import path

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('evaluation', views.EvaluationViewSet)

urlpatterns = [
    path('evaluator/', views.EvaluationList.as_view()),
    path('submit_evaluation/', views.EvaluationSubmission.as_view(),
         name="evaluation_submission"),
]

urlpatterns += router.urls
