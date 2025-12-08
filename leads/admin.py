from django.contrib import admin
from .models import Cafe, SearchQuery


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'source', 'instagram_handle', 'tiktok_handle', 'created_at')
    list_filter = ('source', 'city', 'created_at')
    search_fields = ('name', 'city', 'address', 'instagram_handle', 'tiktok_handle')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'city', 'address', 'website')
        }),
        ('Social Media', {
            'fields': ('instagram_handle', 'tiktok_handle')
        }),
        ('Source Information', {
            'fields': ('source', 'google_place_id', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query_text', 'platform', 'status', 'created_by', 'created_at')
    list_filter = ('platform', 'status', 'created_at')
    search_fields = ('query_text',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Query Information', {
            'fields': ('query_text', 'platform', 'status')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at')
        }),
    )




