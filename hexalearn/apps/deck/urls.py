from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DeckViewSet,
    CardViewSet,
    FolderViewSet,
    get_upload_credential,
)
router = DefaultRouter()
app_name = 'deck'

router.register('folders', FolderViewSet, basename='folder')
router.register('decks', DeckViewSet, basename='deck')
router.register('cards', CardViewSet, basename='card')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('upload-credential/', get_upload_credential, name='upload-credential'),
]