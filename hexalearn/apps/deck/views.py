# apps/deck/views.py
import hashlib
import time
import uuid
from django.db.models import Q

import boto3
import cloudinary
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.home.pagination import CustomPagination

from .models import Card, Deck, Folder, StudyState
from apps.home.models import Source
from .serializers import (
    CardCreateSerializer,
    CardUpdateSerializer,
    DeckCreateSerialzier,
    DeckDetailSerializer,
    DeckUpdateSerializer,
    FolderDetailSerializer,
    FolderListSerializer,
    FolderWriteSerializer,
    # StudyStateSerializer,
)


# ─── UPLOAD CREDENTIAL ──────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upload_credential(request):
    file_name = request.query_params.get('file_name', 'image')
    file_type = request.query_params.get('file_type', 'image/jpeg')
    storage_backend = settings.STORAGES['default']['BACKEND']

    if 'cloudinary' in storage_backend:
        # Dev → Cloudinary signed upload
        timestamp = int(time.time())
        folder = "flashcard"
        params = f"folder={folder}&timestamp={timestamp}{cloudinary.config().api_secret}"
        signature = hashlib.sha1(params.encode()).hexdigest()
        return Response({
            "provider": "cloudinary",
            "signature": signature,
            "timestamp": timestamp,
            "folder": folder,
            "cloud_name": cloudinary.config().cloud_name,
            "api_key": cloudinary.config().api_key,
        })

    else:
        # Prod → AWS S3 presigned URL
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        key = f"flashcard/{uuid.uuid4()}_{file_name}"
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': key,
                'ContentType': file_type,
            },
            ExpiresIn=300  # hết hạn sau 5 phút
        )
        file_url = (
            f"https://{settings.AWS_STORAGE_BUCKET_NAME}"
            f".s3.{settings.AWS_S3_REGION_NAME}"
            f".amazonaws.com/{key}"
        )
        return Response({
            "provider": "s3",
            "presigned_url": presigned_url,
            "file_url": file_url,
        })


# ─── FOLDER ─────────────────────────────────────────────────────────────────
@extend_schema(tags=['Flashcard'])
class FolderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return FolderListSerializer
        if self.action == 'retrieve':
            return FolderDetailSerializer
        return FolderWriteSerializer

    def get_queryset(self):
        return Folder.objects.filter(
            owner=self.request.user
        ).prefetch_related('decks')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# ─── DECK ────────────────────────────────────────────────────────────────────
@extend_schema(tags=['Flashcard'])
class DeckViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DeckDetailSerializer
        if self.action == 'create':
            return DeckCreateSerialzier
        if self.action in ['update', 'partial_update']:
            return DeckUpdateSerializer
        return DeckDetailSerializer
    
    #get all created deck of each user
    def get_queryset(self):
        queryset = Deck.objects.filter(
            owner=self.request.user
        ).prefetch_related('cards')

        return queryset

    def perform_create(self, serializer):
        source = Source.objects.filter(name__iexact='user').first()
        serializer.save(owner=self.request.user, source=source)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# ─── CARD ────────────────────────────────────────────────────────────────────
@extend_schema(tags=['Flashcard'])
class CardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CardUpdateSerializer
        return CardCreateSerializer

    def perform_create(self, serializer):
        deck_id = self.request.data.get('deck_id')
        deck = get_object_or_404(Deck, pk=deck_id, owner=self.request.user)
        serializer.save(deck=deck)

    def create(self, request, *args, **kwargs):
        deck_id = request.data.get('deck_id')
        deck = get_object_or_404(Deck, pk=deck_id, owner=request.user)

        cards_data = request.data.get('cards', None)

        # if upload multiple cards at once
        if isinstance(cards_data, list):
            serializer = CardCreateSerializer(
                data=cards_data,
                many=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            cards = [
                Card(deck=deck, **card_data)
                for card_data in serializer.validated_data
            ]
            Card.objects.bulk_create(cards)
            return Response(
                CardCreateSerializer(cards, many=True).data,
                status=status.HTTP_201_CREATED
            )

        # if upload single card
        serializer = CardCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(deck=deck)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


# ─── STUDY STATE ─────────────────────────────────────────────────────────────

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def due_cards(request):
#     """Lấy danh sách card cần ôn hôm nay"""
#     from django.utils import timezone
#     states = StudyState.objects.filter(
#         user=request.user,
#         next_review__lte=timezone.now().date()
#     ).select_related('card', 'card__deck')

#     serializer = StudyStateSerializer(states, many=True)
#     return Response(serializer.data)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def submit_review(request, card_id):
#     """User submit kết quả ôn 1 card"""
#     from datetime import timedelta
#     from django.utils import timezone

#     result = request.data.get('result')  # True = nhớ, False = không nhớ
#     if result is None:
#         return Response(
#             {"detail": "result is required."},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     card = get_object_or_404(Card, pk=card_id, deck__owner=request.user)
#     state, _ = StudyState.objects.get_or_create(
#         user=request.user,
#         card=card,
#     )

#     # Tính interval mới theo SM-2 binary
#     if result:
#         if state.repetition == 0:
#             state.interval_days = 1
#         elif state.repetition == 1:
#             state.interval_days = 6
#         else:
#             state.interval_days = state.interval_days * 2
#         state.repetition += 1
#     else:
#         state.repetition = 0
#         state.interval_days = 1

#     state.next_review = timezone.now().date() + timedelta(days=state.interval_days)
#     state.last_reviewed = timezone.now()
#     state.last_result = result
#     state.review_count += 1
#     state.save()

#     serializer = StudyStateSerializer(state)
#     return Response(serializer.data)