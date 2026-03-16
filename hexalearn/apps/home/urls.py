from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.home.views import LevelViewSet, SourceViewSet, UserProfileView, AvatarUploadView, RegisterView, DeleteAccountView

router = DefaultRouter()
app_name = 'home'

router.register('levels', LevelViewSet, basename='level')
router.register('sources', SourceViewSet, basename='source')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='profile-avatar'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]
