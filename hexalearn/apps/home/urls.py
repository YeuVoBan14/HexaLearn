from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.home.views import LevelViewSet

router = DefaultRouter()
app_name = 'home'

router.register('levels', LevelViewSet, basename='level')

urlpatterns = [
    path('v1/', include(router.urls)),
]