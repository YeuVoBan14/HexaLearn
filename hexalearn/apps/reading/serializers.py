from .models import Topic, Passage, Paragraph, ParagraphTranslation, ReadingNote, UserReadingProgress
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from drf_spectacular.utils import extend_schema_field, OpenApiTypes

from apps.home.models import Language

from .tasks import detect_vocabulary_for_paragraph_task, detect_vocabulary_for_passage_task

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']
        
# ----------------------------------------------------------------------------
# READ NESTED PASSAGE, PARAGRAPH AND TRANSLATIONS
# ----------------------------------------------------------------------------
class ParagraphTranslationReadSerializer(serializers.ModelSerializer):
    language_code = serializers.CharField(source='language.code', read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
 
    class Meta:
        model  = ParagraphTranslation
        fields = ['id', 'language', 'language_code', 'language_name', 'translation', 'created_at']
        
class ParagraphReadSerializer(serializers.ModelSerializer):
    translations = ParagraphTranslationReadSerializer(many=True, read_only=True)
    image_url    = serializers.SerializerMethodField()
 
    class Meta:
        model  = Paragraph
        fields = [
            'id', 'index', 'content', 'note',
            'image_url', 'translations',
            'created_at', 'updated_at',
        ]
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_url(self, obj) -> str | None:
        return obj.image_url
    
class PassageReadSerializer(serializers.ModelSerializer):
    paragraphs    = ParagraphReadSerializer(many=True, read_only=True)
    language_name = serializers.CharField(source='language.name', read_only=True)
    level_name    = serializers.CharField(source='level.name',    read_only=True)
    topic_name    = serializers.CharField(source='topic.name',    read_only=True)
    image_url     = serializers.SerializerMethodField()
 
    class Meta:
        model  = Passage
        fields = [
            'id', 'title', 'description',
            'language', 'language_name',
            'level', 'level_name',
            'topic', 'topic_name',
            'source', 'estimated_read_time',
            'image_url', 'paragraphs',
            'created_at', 'updated_at',
        ]
 
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_url(self, obj) -> str | None:
        return obj.image_url
   
# ----------------------------------------------------------------------------
# WRITE NESTED PASSAGE
# ---------------------------------------------------------------------------- 
class ParagraphTranslationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ParagraphTranslation
        fields = ['language', 'translation']

class ParagraphWriteSerializer(serializers.ModelSerializer):
    """
    Dùng cho standalone create/update paragraph.
    Nếu muốn tạo kèm translation:
        { "content": "...", "translation": { "language": 1, "translation": "..." } }
    """
    translation = ParagraphTranslationWriteSerializer(
        write_only=True, required=False, allow_null=True
    )
    
    class Meta:
        model  = Paragraph
        fields = ['image', 'content', 'note', 'translation']
        
    def create(self, validated_data):
        translation_data = validated_data.pop('translation', None)

        paragraph = Paragraph.objects.create(**validated_data)

        # Tạo translation được cung cấp
        provided_language_id = None
        if translation_data:
            provided_language_id = translation_data['language'].pk
            ParagraphTranslation.objects.create(
                paragraph=paragraph,
                **translation_data,
            )

        # Tìm các language còn thiếu trong passage → tạo placeholder
        existing_languages = Language.objects.filter(
            paragraphtranslation__paragraph__passage=paragraph.passage
        ).distinct()

        for language in existing_languages:
            if language.pk == provided_language_id:
                continue
            ParagraphTranslation.objects.get_or_create(
                paragraph=paragraph,
                language=language,
                defaults={'translation': f"No translation in {language.name} yet"},
            )

        transaction.on_commit(
            lambda: detect_vocabulary_for_paragraph_task.delay(paragraph.pk)
        )
        return paragraph

    def update(self, instance, validated_data):
        # Translation không update qua đây — dùng action translation_update
        validated_data.pop('translation', None)

        content_changed = (
            'content' in validated_data and
            validated_data['content'] != instance.content
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if content_changed:
            transaction.on_commit(
                lambda: detect_vocabulary_for_paragraph_task.delay(instance.pk, replace=True)
            )
        return instance
    
class _ParagraphInPassageSerializer(serializers.ModelSerializer):
    """
    local serializer ussed for nested create paragraphs in passage.
    translation is only a string because the language is provided at the passage level.
    """
    translation = serializers.CharField(write_only=True, required=False, allow_null=True)
 
    class Meta:
        model  = Paragraph
        fields = ['image', 'content', 'note', 'translation']
        
class PassageWriteSerializer(serializers.ModelSerializer):
    """
    - Obtain 'translation_language' at passsage level, apply to all paragraphs.
    - Which any paragraph has translation provided, it will be created. For those don't have, a placeholder will be created with "No translation in {language.name} yet".
    - Update only updates the basic information of the passage, not the paragraphs.
    """
    paragraphs = _ParagraphInPassageSerializer(
        many=True, required=False, write_only=True
    )
    translation_language = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    class Meta:
        model  = Passage
        fields = [
            'title', 'language', 'description', 'cover_image',
            'level', 'topic', 'source', 'estimated_read_time',
            'paragraphs', 'translation_language',
        ]
        
    @transaction.atomic
    def create(self, validated_data):
        paragraphs_data      = validated_data.pop('paragraphs', [])
        translation_language = validated_data.pop('translation_language', None)
 
        passage = Passage.objects.create(**validated_data)
 
        for para_data in paragraphs_data:
            translation_text = para_data.pop('translation', None)
            paragraph = Paragraph.objects.create(passage=passage, **para_data)
 
            # always create translation if translation_language provided.
            # paragraph which not provide translation will have a placeholder.
            if translation_language:
                ParagraphTranslation.objects.create(
                    paragraph=paragraph,
                    language=translation_language,
                    translation=translation_text or f"No translation in {translation_language.name} yet",
                )
 
        if paragraphs_data:
            transaction.on_commit(
                lambda: detect_vocabulary_for_passage_task.delay(passage.pk)
            )
 
        return passage
 
    @transaction.atomic
    def update(self, instance, validated_data):
        # Only update passage's basic info, not paragraphs.
        validated_data.pop('paragraphs', None)
        validated_data.pop('translation_language', None)
 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
            
        
    
        

    