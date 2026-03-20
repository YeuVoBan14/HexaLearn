from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DeckViewSet,
    CardViewSet,
    FolderViewSet,
)
router = DefaultRouter()
app_name = 'deck'

router.register('folders', FolderViewSet, basename='folder')
router.register('decks', DeckViewSet, basename='deck')
router.register('cards', CardViewSet, basename='card')

urlpatterns = [
    path('v1/', include(router.urls)),
]