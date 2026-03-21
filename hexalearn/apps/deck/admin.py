from django.contrib import admin
from .models import Card, Deck, Folder, StudyState


# ─── INLINES ─────────────────────────────────────────────────────────────────

class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    fields = ['front_text', 'back_text', 'hint', 'front_image', 'back_image', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True


class DeckInline(admin.TabularInline):
    model = Deck
    extra = 0
    fields = ['title', 'is_public', 'estimated_level', 'source', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True


# ─── CARD ────────────────────────────────────────────────────────────────────

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'front_text', 'back_text', 'deck', 'created_at']
    list_filter = ['deck__estimated_level', 'created_at']
    search_fields = ['front_text', 'back_text', 'deck__title']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Content', {
            'fields': ('deck', 'front_text', 'back_text', 'hint')
        }),
        ('Images', {
            'fields': ('front_image', 'back_image'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ─── DECK ────────────────────────────────────────────────────────────────────

@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'owner', 'folder', 'source', 'estimated_level', 'is_public', 'card_count', 'created_at']
    list_filter = ['is_public', 'estimated_level', 'source', 'created_at']
    search_fields = ['title', 'owner__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['owner', 'folder']
    inlines = [CardInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'folder', 'title', 'description')
        }),
        ('Settings', {
            'fields': ('source', 'estimated_level', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Cards')
    def card_count(self, obj):
        return obj.cards.count()


# ─── FOLDER ──────────────────────────────────────────────────────────────────

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'deck_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['owner']
    inlines = [DeckInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Decks')
    def deck_count(self, obj):
        return obj.decks.count()