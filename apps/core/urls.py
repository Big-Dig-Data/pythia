from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('user/password-reset', views.UserPasswordResetView.as_view(), name='user_password_reset'),
    path('info/', views.SystemInfoView.as_view(), name='system_info_api_view'),
]
