from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework import viewsets, status

from .models import (Kanji, KanjiMeaning, PartOfSpeech, Word, WordMeaning, WordPronunciation, WordImage, KanjiWord, Example)
from apps.home.pagination import CustomPagination
from .serializers import (KanjiSerializer, KanjiSuggestSerializer, KanjiWriteSerializer, PartOfSpeechSerializer,
                        WordSerializer, WordSuggestSerializer, WordWriteSerializer,
                        WordMeaningWriteSerializer, WordMeaningSerializer,
                        WordPronunciationWriteSerializer, WordPronunciationSerializer,
                        WordImageWriteSerializer, WordImageSerializer,
                        ExampleWriteSerializer, ExampleSerializer,
                        KanjiWordWriteSerializer, KanjiWordInlineSerializer,
                        KanjiMeaningWriteSerializer, KanjiMeaningSerializer)
from .docs import *
from apps.home.models import MediaFile
from apps.account.storage import delete_media_file, delete_media_files_bulk

# Create your views here.
@part_of_speech_schema()
class PartOfSpeechViewSet(viewsets.ModelViewSet):
    queryset = PartOfSpeech.objects.all()
    serializer_class = PartOfSpeechSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

@word_schema()
class WordViewSet(viewsets.ModelViewSet):
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    pagination_class   = CustomPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]
    
    def get_queryset(self):
        return Word.objects.prefetch_related(
            'meanings', 'pronunciations', 'word_images__media_file',
            'kanji_words__kanji', 'examples'
        ).select_related('language', 'level', 'part_of_speech')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WordWriteSerializer
        return WordSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = WordWriteSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        write_serializer.is_valid(raise_exception=True)
        word = write_serializer.save()

        read_serializer = WordSerializer(
            word,
            context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        word = self.get_object()
        media_files = MediaFile.objects.filter(word_images__word=word)
 
        # Delete all files in cloud and related media files
        # WordImage will be automated deleted with Word (CASCADE)
        delete_media_files_bulk(media_files)
 
        word.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @word_suggest_schema()
    @action(detail=False, methods=['get'], url_path='suggest')
    def suggest(self, request):
        search = request.query_params.get('search', '').strip()
        if len(search) < 1:
            return Response([])

        words = Word.objects.filter(
            Q(lemma__icontains=search) |
            Q(pronunciations__pronunciation__icontains=search) |
            Q(meanings__short_definition__icontains=search)
        ).select_related(
            'language', 'part_of_speech'
        ).prefetch_related(
            'meanings'
        ).distinct()[:10]

        serializer = WordSuggestSerializer(words, many=True, context={'request': request})
        return Response(serializer.data)

@word_meaning_schema()
class WordMeaningViewSet(viewsets.ModelViewSet):
    """
    GET /words/{word_pk}/meanings/          - list of word meanings
    POST /words/{word__pk}/meanings/        - add new meanings
    PATCH /words/{word__pk}/meanings/{id}/  - edit meaning
    DELETE /words/{word_pk}/meanings{id}/   - delete meaning
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return WordMeaning.objects.filter(
            word_id=self.kwargs['word_pk']
        ).select_related('language')
        
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return WordMeaningWriteSerializer
        return WordMeaningSerializer
    
    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        serializer.save(word=word)
        
@word_pronunciation_schema()
class WordPronunciationViewSet(viewsets.ModelViewSet):
    """
    GET    /words/{word_pk}/pronunciations/
    POST   /words/{word_pk}/pronunciations/
    PATCH  /words/{word_pk}/pronunciations/{id}/
    DELETE /words/{word_pk}/pronunciations/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return WordPronunciation.objects.filter(word_id=self.kwargs['word_pk']).order_by('id')

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return WordPronunciationWriteSerializer
        return WordPronunciationSerializer

    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        serializer.save(word=word)
        
@word_image_schema()
class WordImageViewSet(viewsets.ModelViewSet):
    """
    GET    /words/{word_pk}/images/
    POST   /words/{word_pk}/images/        — nhận metadata Cloudinary/S3
    DELETE /words/{word_pk}/images/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return WordImage.objects.filter(
            word_id=self.kwargs['word_pk']
        ).select_related('media_file').order_by("id")

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return WordImageWriteSerializer
        return WordImageSerializer

    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        data = serializer.validated_data
        media_file = MediaFile.objects.create(
            file_url  = data['file_url'],
            file_path = data['file_path'],
            file_name = data['file_name'],
            mime_type = data['mime_type'],
            alt_text  = data.get('alt_text', ''),
            file_size = data.get('file_size'),
            upload_by = self.request.user,
        )
        WordImage.objects.create(word=word, media_file=media_file)
        
    def destroy(self, request, *args, **kwargs):
        word_image = self.get_object()
        media_file = word_image.media_file
 
        word_image.delete()
 
        # Xóa file trên cloud + MediaFile trong DB
        delete_media_file(media_file)
 
        return Response(status=status.HTTP_204_NO_CONTENT)
        
@word_example_schema()
class WordExampleViewSet(viewsets.ModelViewSet):
    """
    GET    /words/{word_pk}/examples/
    POST   /words/{word_pk}/examples/
    PATCH  /words/{word_pk}/examples/{id}/
    DELETE /words/{word_pk}/examples/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return Example.objects.filter(
            word_id=self.kwargs['word_pk']
        ).select_related('language', 'language_of_translation').order_by("id")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return ExampleWriteSerializer
        return ExampleSerializer

    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        serializer.save(word=word)
        
@word_kanji_schema()
class WordKanjiWordViewSet(viewsets.ModelViewSet):
    """
    GET    /words/{word_pk}/kanjis/
    POST   /words/{word_pk}/kanjis/
    PATCH  /words/{word_pk}/kanjis/{id}/
    DELETE /words/{word_pk}/kanjis/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return KanjiWord.objects.filter(
            word_id=self.kwargs['word_pk']
        ).select_related('kanji').order_by("id")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return KanjiWordWriteSerializer
        return KanjiWordInlineSerializer

    def perform_create(self, serializer):
        word = Word.objects.get(pk=self.kwargs['word_pk'])
        serializer.save(word=word)

# ---------------------------------------------------------------------------
# KANJI VIEWSET
# ---------------------------------------------------------------------------
@kanji_schema()
class KanjiViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    pagination_class   = CustomPagination
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]
    def get_queryset(self):
        return Kanji.objects.prefetch_related(
            'meanings', 'examples'
        ).select_related('level').order_by("id")

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return KanjiWriteSerializer
        return KanjiSerializer

    @kanji_suggest_schema()
    @action(detail=False, methods=['get'], url_path='suggest')
    def suggest(self, request):
        search = request.query_params.get('search', '').strip()
        if len(search) < 1:
            return Response([])

        kanjis = Kanji.objects.filter(
            Q(character__icontains=search) |
            Q(onyomi__icontains=search)    |
            Q(kunyomi__icontains=search)   |
            Q(meanings__meaning__icontains=search)
        ).select_related(
            'level'
        ).prefetch_related(
            'meanings'
        ).distinct()[:10]

        serializer = KanjiSuggestSerializer(kanjis, many=True, context={'request': request})
        return Response(serializer.data)
    
@kanji_meaning_schema()
class KanjiMeaningViewSet(viewsets.ModelViewSet):
    """
    GET    /kanjis/{kanji_pk}/meanings/
    POST   /kanjis/{kanji_pk}/meanings/
    PATCH  /kanjis/{kanji_pk}/meanings/{id}/
    DELETE /kanjis/{kanji_pk}/meanings/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return KanjiMeaning.objects.filter(
            kanji_id=self.kwargs['kanji_pk']
        ).select_related('language').order_by("id")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return KanjiMeaningWriteSerializer
        return KanjiMeaningSerializer

    def perform_create(self, serializer):
        kanji = Kanji.objects.get(pk=self.kwargs['kanji_pk'])
        serializer.save(kanji=kanji)

@kanji_example_schema()
class KanjiExampleViewSet(viewsets.ModelViewSet):
    """
    GET    /kanjis/{kanji_pk}/examples/
    POST   /kanjis/{kanji_pk}/examples/
    PATCH  /kanjis/{kanji_pk}/examples/{id}/
    DELETE /kanjis/{kanji_pk}/examples/{id}/
    """
    lookup_value_regex = r'\d+'
    http_method_names  = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Example.objects.filter(
            kanji_id=self.kwargs['kanji_pk']
        ).select_related('language', 'language_of_translation').order_by("id")

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return ExampleWriteSerializer
        return ExampleSerializer

    def perform_create(self, serializer):
        kanji = Kanji.objects.get(pk=self.kwargs['kanji_pk'])
        serializer.save(kanji=kanji)
    
