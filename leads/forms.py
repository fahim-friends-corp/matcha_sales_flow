from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cafe


# SignUpForm removed - accounts created via admin panel only
# class SignUpForm(UserCreationForm):
#     """
#     Custom user registration form with email field.
#     DISABLED - Create users via Django admin panel instead.
#     """
#     pass


class GoogleMapsSearchForm(forms.Form):
    """
    Form for searching Google Maps/Places.
    """
    query = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., matcha café in Tokyo'
        }),
        label='Search Query'
    )


class ApifySearchForm(forms.Form):
    """
    Form for searching TikTok/Instagram via Apify.
    Supports different search types: profiles, hashtags, and places.
    """
    PLATFORM_CHOICES = [
        ('tiktok', 'TikTok'),
        ('instagram', 'Instagram'),
    ]
    
    SEARCH_TYPE_CHOICES = [
        ('profile', 'Profile/Username'),
        ('hashtag', 'Hashtag'),
        ('place', 'Place/Location'),
    ]
    
    platform = forms.ChoiceField(
        choices=PLATFORM_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'platform-select'
        }),
        label='Platform'
    )
    
    search_type = forms.ChoiceField(
        choices=SEARCH_TYPE_CHOICES,
        required=True,
        initial='profile',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'search-type-select'
        }),
        label='Search Type'
    )
    
    query = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., starbucks (for profile) or Tokyo (for place)',
            'id': 'query-input'
        }),
        label='Search Query',
        help_text='Enter usernames (without @), hashtags (without #), or place names'
    )


class CafeUpdateForm(forms.ModelForm):
    """
    Form for updating café information.
    """
    class Meta:
        model = Cafe
        fields = ['name', 'city', 'address', 'website', 'instagram_handle', 'tiktok_handle', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram_handle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'username (without @)'
            }),
            'tiktok_handle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'username (without @)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }


class CafeFilterForm(forms.Form):
    """
    Form for filtering café list.
    """
    SOURCE_CHOICES = [
        ('', 'All Sources'),
        ('google_maps', 'Google Maps'),
        ('apify_tiktok', 'Apify TikTok'),
        ('apify_instagram', 'Apify Instagram'),
        ('manual', 'Manual Entry'),
    ]
    
    source = forms.ChoiceField(
        choices=SOURCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Source'
    )
    
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by city'
        }),
        label='City'
    )




