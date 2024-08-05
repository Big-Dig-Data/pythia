from django.urls import path, include

from rest_framework import routers

from . import views

app_name = "aleph"

router = routers.DefaultRouter()
router.register(r'entries', views.AlephEntryViewSet)

urlpatterns = [
    # REST API
    path('', include(router.urls))
]
