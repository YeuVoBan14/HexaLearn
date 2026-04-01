from django.contrib import admin
from .models import Passage, Paragraph, ParagraphTranslation, Topic

# Register your models here.


class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


class ParagraphTranslationInline(admin.TabularInline):
    model = ParagraphTranslation
    extra = 0
    fields = ('language', 'translation')
    verbose_name = 'Translation'
    verbose_name_plural = 'Translations'


class ParagraphInline(admin.StackedInline):
    model = Paragraph
    extra = 0
    fields = ('index', 'content', 'note', 'image', 'translation_languages')
    readonly_fields = ('translation_languages',)
    show_change_link = True

    def translation_languages(self, obj):
        if not obj or not obj.pk:
            return '-'
        languages = obj.translations.values_list(
            'language__name', flat=True).distinct()
        return ', '.join(languages) if languages else '-'
    translation_languages.short_description = 'Translation Languages'


class PassageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'language', 'level',
                    'topic', 'translation_languages')
    search_fields = ('title', 'description', 'topic__name', 'source__name')
    list_filter = ('language', 'level', 'topic')
    inlines = (ParagraphInline,)

    def translation_languages(self, obj):
        languages = obj.paragraphs.filter(translations__isnull=False).values_list(
            'translations__language__name', flat=True
        ).distinct()
        return ', '.join(languages) if languages else '-'
    translation_languages.short_description = 'Translation Languages'


class ParagraphAdmin(admin.ModelAdmin):
    list_display = ('id', 'passage', 'index',
                    'content_preview', 'translation_languages')
    list_filter = ('passage',)
    search_fields = ('content', 'note', 'passage__title')
    inlines = (ParagraphTranslationInline,)
    raw_id_fields = ('passage',)

    def content_preview(self, obj):
        return obj.content[:80] + '...' if obj.content and len(obj.content) > 80 else obj.content
    content_preview.short_description = 'Content Preview'

    def translation_languages(self, obj):
        languages = obj.translations.values_list(
            'language__name', flat=True).distinct()
        return ', '.join(languages) if languages else '-'
    translation_languages.short_description = 'Translation Languages'


class PassageTranslationAdmin(admin.ModelAdmin):
    list_display = ('id', 'paragraph', 'language', 'created_at')
    list_filter = ('language',)
    search_fields = ('paragraph__passage__title',
                     'paragraph__content', 'language__name')


admin.site.register(Passage, PassageAdmin)
admin.site.register(Paragraph, ParagraphAdmin)
admin.site.register(ParagraphTranslation, PassageTranslationAdmin)
admin.site.register(Topic, TopicAdmin)
