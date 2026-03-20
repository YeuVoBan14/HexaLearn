# apps/accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, MeView, get_upload_credential

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view()),
    path('me/', MeView.as_view()),
    path('upload-credential/', get_upload_credential, name='upload-credential'),
]