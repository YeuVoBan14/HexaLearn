from django.contrib import admin
from .models import (
    PartOfSpeech,
    Word,
    WordMeaning,
    WordPronunciation,
    WordImage,
    Kanji,
    KanjiMeaning,
    KanjiWord,
    Example,
    SavedWordList,
    SavedWordListItem,
    UserPinnedWord
)


# =========================
# Inlines for Word
# =========================
class WordMeaningInline(admin.TabularInline):
    model = WordMeaning
    extra = 0
    fields = ("language", "short_definition", "full_definition", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


class WordPronunciationInline(admin.TabularInline):
    model = WordPronunciation
    extra = 0
    fields = ("type", "pronunciation", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


class WordImageInline(admin.TabularInline):
    model = WordImage
    extra = 0
    fields = ("created_at",)
    readonly_fields = ("created_at",)
    show_change_link = True


class KanjiWordInlineForWord(admin.TabularInline):
    model = KanjiWord
    extra = 0
    fk_name = "word"
    fields = ("kanji", "position", "reading_in_word", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("kanji",)
    show_change_link = True


class ExampleInlineForWord(admin.TabularInline):
    model = Example
    extra = 0
    fk_name = "word"
    fields = (
        "kanji",
        "sentence",
        "language",
        "translation",
        "language_of_translation",
        "created_at",
    )
    readonly_fields = ("created_at",)
    autocomplete_fields = ("kanji", "language", "language_of_translation")
    show_change_link = True


# =========================
# Inlines for Kanji
# =========================
class KanjiMeaningInline(admin.TabularInline):
    model = KanjiMeaning
    extra = 0
    fields = ("language", "meaning", "created_at")
    readonly_fields = ("created_at",)
    show_change_link = True


class KanjiWordInlineForKanji(admin.TabularInline):
    model = KanjiWord
    extra = 0
    fk_name = "kanji"
    fields = ("word", "position", "reading_in_word", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("word",)
    show_change_link = True


class ExampleInlineForKanji(admin.TabularInline):
    model = Example
    extra = 0
    fk_name = "kanji"
    fields = (
        "word",
        "sentence",
        "language",
        "translation",
        "language_of_translation",
        "created_at",
    )
    readonly_fields = ("created_at",)
    autocomplete_fields = ("word", "language", "language_of_translation")
    show_change_link = True


# =========================
# Main Admins
# =========================
@admin.register(PartOfSpeech)
class PartOfSpeechAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "language", "created_at")
    list_filter = ("language",)
    search_fields = ("name", "code", "language__name", "language__code")
    ordering = ("id", "language__code", "code")
    autocomplete_fields = ("language",)
    list_per_page = 50


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lemma",
        "language",
        "part_of_speech",
        "level",
        "created_at",
        "updated_at",
    )
    list_filter = ("language", "part_of_speech", "level")
    search_fields = ("lemma",)
    ordering = ("lemma",)
    autocomplete_fields = ("language", "level", "part_of_speech")
    list_per_page = 50
    inlines = [
        WordMeaningInline,
        WordPronunciationInline,
        WordImageInline,
        KanjiWordInlineForWord,
        ExampleInlineForWord,
    ]


@admin.register(Kanji)
class KanjiAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "character",
        "level",
        "onyomi",
        "kunyomi",
        "stroke_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("level",)
    search_fields = ("character", "onyomi", "kunyomi")
    ordering = ("character",)
    autocomplete_fields = ("level",)
    list_per_page = 50
    inlines = [
        KanjiMeaningInline,
        KanjiWordInlineForKanji,
        ExampleInlineForKanji,
    ]


# =========================
# Optional: register related models
# =========================
@admin.register(WordMeaning)
class WordMeaningAdmin(admin.ModelAdmin):
    list_display = ("id", "word", "language", "short_definition", "created_at")
    list_filter = ("language",)
    search_fields = ("word__lemma", "short_definition", "full_definition")
    autocomplete_fields = ("word", "language")
    list_per_page = 50


@admin.register(WordPronunciation)
class WordPronunciationAdmin(admin.ModelAdmin):
    list_display = ("id", "word", "type", "pronunciation", "created_at")
    list_filter = ("type",)
    search_fields = ("word__lemma", "pronunciation")
    autocomplete_fields = ("word",)
    list_per_page = 50

@admin.register(WordImage)
class WordImageAdmin(admin.ModelAdmin):
    list_display = ("id", "media_file")
    list_per_page = 50

@admin.register(KanjiMeaning)
class KanjiMeaningAdmin(admin.ModelAdmin):
    list_display = ("id", "kanji", "language", "meaning", "created_at")
    list_filter = ("language",)
    search_fields = ("kanji__character", "meaning")
    autocomplete_fields = ("kanji", "language")
    list_per_page = 50


@admin.register(KanjiWord)
class KanjiWordAdmin(admin.ModelAdmin):
    list_display = ("id", "kanji", "word", "position", "reading_in_word", "created_at")
    list_filter = ()
    search_fields = ("kanji__character", "word__lemma", "reading_in_word")
    autocomplete_fields = ("kanji", "word")
    list_per_page = 50


@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "word",
        "kanji",
        "short_sentence",
        "language",
        "language_of_translation",
        "created_at",
    )
    list_filter = ("language", "language_of_translation")
    search_fields = ("sentence", "translation", "word__lemma", "kanji__character")
    autocomplete_fields = ("word", "kanji", "language", "language_of_translation")
    list_per_page = 50

    @admin.display(description="Sentence")
    def short_sentence(self, obj):
        return obj.sentence[:50] + "..." if len(obj.sentence) > 50 else obj.sentence
    
class SavedWordListItemInline(admin.TabularInline):
    model = SavedWordListItem
    extra = 0
    autocomplete_fields = ['word']
    fields = ('word', 'position')
    ordering = ('position',)
    show_change_link = True


@admin.register(SavedWordList)
class SavedWordListAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'is_public', 'word_count', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    autocomplete_fields = ['user']
    inlines = [SavedWordListItemInline]
    ordering = ('-created_at',)

    @admin.display(description='Words')
    def word_count(self, obj):
        return obj.items.count()


@admin.register(UserPinnedWord)
class UserPinnedWordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'word')
    search_fields = (
        'user__username',
        'word__lemma',
        'word__language__name',
    )
    autocomplete_fields = ['user', 'word']
    ordering = ('-id',)