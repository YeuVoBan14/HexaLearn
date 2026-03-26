from django.contrib import admin
from .models import Language, Level, Source, UserProfile, MediaFile
# Register your models here.


class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'native_language',
                    'daily_ai_limit', 'reading_level')
    search_fields = ('user__username', 'native_language')
    list_filter = ('native_language', 'reading_level')


class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'difficulty_rank')
    search_fields = ('name', 'code')
    list_filter = ('difficulty_rank',)


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'mime_type', 'file_size',
                    'upload_by', 'created_at')
    search_fields = ('file_name', 'mime_type', 'alt_text')
    list_filter = ('mime_type', 'created_at', 'upload_by')
    readonly_fields = ('created_at',)


admin.site.register(Language, LanguageAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(MediaFile, MediaFileAdmin)
