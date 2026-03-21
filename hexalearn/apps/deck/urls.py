from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DeckViewSet,
    CardViewSet,
    FolderViewSet,
    decks_in_progress,
    study_session,
    study_stats,
    submit_review,
)
router = DefaultRouter()
app_name = 'deck'

router.register('folders', FolderViewSet, basename='folder')
router.register('decks', DeckViewSet, basename='deck')
router.register('cards', CardViewSet, basename='card')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('study/in-progress/', decks_in_progress, name='decks-in-progress'),
    path('study/session/', study_session, name='study-session'),
    path('study/submit/<int:card_id>/', submit_review, name='submit-review'),
    path('study/stats/', study_stats, name='study-stats'),
]