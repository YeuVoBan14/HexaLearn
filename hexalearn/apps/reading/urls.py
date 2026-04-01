from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers
 
from .views import TopicViewSet, PassageViewSet, ParagraphViewSet
 
router = DefaultRouter()
router.register(r'topics',   TopicViewSet,   basename='topic')
router.register(r'passages', PassageViewSet, basename='passage')
 
# /passages/{passage_pk}/paragraphs/
passage_router = nested_routers.NestedDefaultRouter(router, r'passages', lookup='passage')
passage_router.register(r'paragraphs', ParagraphViewSet, basename='passage-paragraph')
 
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(passage_router.urls)),
]