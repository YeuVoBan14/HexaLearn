# apps/deck/views.py

from django.db.models import Q


from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.home.pagination import CustomPagination

from .models import Card, Deck, Folder, StudyState
from apps.home.models import Source
from .serializers import (
    CardSerializer,
    DeckCreateSerializer,
    DeckDetailSerializer,
    DeckOverviewSerializer,
    DeckUpdateSerializer,
    FolderSerializer,
    # StudyStateSerializer,
)


# ─── FOLDER ─────────────────────────────────────────────────────────────────
@extend_schema(tags=['Flashcard'])
class FolderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = FolderSerializer

    def get_queryset(self):
        queryset = Folder.objects.filter(
            owner=self.request.user
        ).prefetch_related('decks')

        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='overview')
    def overview(self, request):
        folders = Folder.objects.filter(
            owner=request.user
        ).prefetch_related('decks')

        unorganized_decks = Deck.objects.filter(
            owner=request.user,
            folder=None
        )

        serializer = DeckOverviewSerializer({
            "folders": folders,
            "unorganized_decks": unorganized_decks,
        })

        return Response(serializer.data)
# ─── DECK ────────────────────────────────────────────────────────────────────
@extend_schema(tags=['Flashcard'])
class DeckViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'put', 'delete']
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DeckDetailSerializer
        if self.action == 'create':
            return DeckCreateSerializer
        if self.action in ['update', 'partial_update']:
            return DeckUpdateSerializer
        return DeckDetailSerializer

    # get all created deck of each user
    def get_queryset(self):
        if self.action == 'list':
            # if list, only show public deck of all users
            queryset = Deck.objects.filter(is_public=True)
        else:
            # Retrieve public deck and private deck of the user
            queryset = Deck.objects.filter(
                Q(owner=self.request.user) | Q(is_public=True)
            ).prefetch_related('cards')

        name = self.request.query_params.get('name')
        source = self.request.query_params.get('source')
        level = self.request.query_params.get('level')

        if name:
            queryset = queryset.filter(title__icontains=name)
        if source:
            queryset = queryset.filter(source__code=source)
        if level:
            queryset = queryset.filter(estimated_level__code=level)

        return queryset

    
    def get_object(self):
        obj = super().get_object()
        if self.action in ['update', 'partial_update', 'destroy']:
            if obj.owner != self.request.user:
                raise PermissionDenied(
                    "You do not have permission to modify this deck.")
        return obj

    def perform_create(self, serializer):
        source = Source.objects.filter(name__iexact='user').first()
        serializer.save(owner=self.request.user, source=source)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], url_path='copy')
    def copy(self, request, pk=None):
        deck = get_object_or_404(Deck, pk=pk, is_public=True)

        # create a copy of the deck for the user
        new_deck = Deck.objects.create(
            owner=request.user,
            title=f"{deck.title} (copy)",
            description=deck.description,
            source=deck.source,
            estimated_level=deck.estimated_level,
            is_public=False,  # default to private, user can change it later if they want
        )

        # Copy toàn bộ cards
        Card.objects.bulk_create([
            Card(
                deck=new_deck,
                front_text=card.front_text,
                back_text=card.back_text,
                hint=card.hint,
                front_image=card.front_image,
                back_image=card.back_image,
            )
            for card in deck.cards.all()
        ])

        return Response(DeckDetailSerializer(new_deck, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

# ─── CARD ────────────────────────────────────────────────────────────────────
@extend_schema(tags=['Flashcard'])
class CardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # dont need pagination and get for card, because we will load all cards of a deck at once
    http_method_names = ['post', 'patch', 'put']
    serializer_class = CardSerializer

    def get_object(self):
        obj = super().get_object()
        if self.action in ['update', 'partial_update']:
            if obj.deck.owner != self.request.user:
                raise PermissionDenied(
                    "You do not have permission to modify this card.")
        return obj

    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed. Get cards via deck."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed. Create cards via deck."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='sync')
    def sync(self, request):
        deck_id = request.data.get('deck_id')
        if not deck_id:
            return Response(
                {"detail": "deck_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deck = get_object_or_404(Deck, pk=deck_id, owner=request.user)

        add_data = request.data.get('add', [])
        delete_ids = request.data.get('delete', [])

        if not add_data and not delete_ids:
            return Response(
                {"detail": "add or delete is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # delete cards
        deleted_count = 0
        if delete_ids:
            cards_to_delete = Card.objects.filter(pk__in=delete_ids, deck=deck)
            deleted_count = cards_to_delete.count()
            cards_to_delete.delete()

        # add new cards
        new_cards = []
        if add_data:
            if not isinstance(add_data, list):
                return Response(
                    {"detail": "add must be a list."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = CardSerializer(
                data=add_data,
                many=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            new_cards = Card.objects.bulk_create([
                Card(deck=deck, **card_data)
                for card_data in serializer.validated_data
            ])

        return Response({
            "deleted": deleted_count,
            "added": CardSerializer(new_cards, many=True).data,
        }, status=status.HTTP_200_OK)


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
