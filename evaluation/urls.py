from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('evaluation', views.EvaluationViewSet)

urlpatterns = []

urlpatterns += router.urls
