from django.db import models
from django.contrib.auth.models import User


class Cafe(models.Model):
    """
    Model to store café leads from various sources (Google Maps, TikTok, Instagram).
    """
    SOURCE_CHOICES = [
        ('google_maps', 'Google Maps'),
        ('apify_tiktok', 'Apify TikTok'),
        ('apify_instagram', 'Apify Instagram'),
        ('manual', 'Manual Entry'),
    ]

    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    instagram_handle = models.CharField(max_length=255, blank=True, null=True)
    tiktok_handle = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    google_place_id = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Café'
        verbose_name_plural = 'Cafés'

    def __str__(self):
        return f"{self.name} ({self.get_source_display()})"


class SearchQuery(models.Model):
    """
    Model to track search queries made to different platforms.
    """
    PLATFORM_CHOICES = [
        ('google_maps', 'Google Maps'),
        ('tiktok', 'TikTok'),
        ('instagram', 'Instagram'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    query_text = models.CharField(max_length=255)
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='done')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'

    def __str__(self):
        return f"{self.query_text} on {self.get_platform_display()} - {self.status}"




