from django.urls import path, include

from rest_framework_nested import routers

from . import views

app_name = "candidates"


router = routers.SimpleRouter()
router.register(r'candidates', views.CandidateViewSet, basename='candidates')
router.register(
    r'candidates_settings', views.CandidatesSettingsViewSet, basename='candidates_settings'
)

urlpatterns = [path('', include(router.urls))]
