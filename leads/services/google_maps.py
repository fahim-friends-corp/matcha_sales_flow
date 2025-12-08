"""
Google Maps Places API integration.

This module provides functions to search for places using the official Google Places API.
Requires GOOGLE_MAPS_API_KEY to be set in environment variables.
"""

import requests
import re
from bs4 import BeautifulSoup
from django.conf import settings
from typing import List, Dict, Optional


def search_places(query: str) -> List[Dict]:
    """
    Calls Google Places API Text Search and returns normalized list of places.
    
    Args:
        query: Search query string (e.g., "matcha café in Tokyo")
    
    Returns:
        List of dictionaries containing place information:
        - name: Business name
        - address: Formatted address
        - website: Website URL (if available)
        - place_id: Google Place ID
        - city: City name (extracted from address components)
    
    Raises:
        ValueError: If API key is not configured
        requests.RequestException: If API call fails
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not configured in settings")
    
    # Google Places API Text Search endpoint
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    params = {
        'query': query,
        'key': api_key,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'OK':
            error_message = data.get('error_message', data.get('status'))
            raise Exception(f"Google Places API error: {error_message}")
        
        results = []
        for place in data.get('results', []):
            # Extract city from address components if available
            city = _extract_city(place.get('address_components', []))
            
            place_data = {
                'name': place.get('name', ''),
                'address': place.get('formatted_address', ''),
                'place_id': place.get('place_id', ''),
                'city': city,
                'website': None,  # Website requires Place Details API call
            }
            
            results.append(place_data)
        
        return results
    
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch data from Google Places API: {str(e)}")


def get_place_details(place_id: str) -> Optional[Dict]:
    """
    Fetches detailed information about a specific place including website.
    
    Args:
        place_id: Google Place ID
    
    Returns:
        Dictionary with detailed place information including website
    """
    api_key = settings.GOOGLE_MAPS_API_KEY
    
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not configured in settings")
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,website,address_components',
        'key': api_key,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'OK':
            return None
        
        result = data.get('result', {})
        city = _extract_city(result.get('address_components', []))
        
        return {
            'name': result.get('name', ''),
            'address': result.get('formatted_address', ''),
            'website': result.get('website'),
            'city': city,
            'place_id': place_id,
        }
    
    except requests.RequestException:
        return None


def _extract_city(address_components: List[Dict]) -> Optional[str]:
    """
    Extracts city name from Google Places address components.
    
    Args:
        address_components: List of address component dictionaries from Google Places API
    
    Returns:
        City name if found, None otherwise
    """
    for component in address_components:
        if 'locality' in component.get('types', []):
            return component.get('long_name')
    
    # Fallback to administrative_area_level_1 (state/province)
    for component in address_components:
        if 'administrative_area_level_1' in component.get('types', []):
            return component.get('long_name')
    
    return None


def extract_instagram_from_website(website_url: str) -> Optional[str]:
    """
    Visits a website and extracts Instagram handle from social media links.
    
    Args:
        website_url: The website URL to scrape
    
    Returns:
        Instagram handle (without @) if found, None otherwise
    """
    if not website_url:
        return None
    
    try:
        # Set a timeout and user agent to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(website_url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Method 1: Look for Instagram links in <a> tags
        instagram_links = soup.find_all('a', href=re.compile(r'instagram\.com', re.IGNORECASE))
        for link in instagram_links:
            href = link.get('href', '')
            handle = _extract_instagram_handle_from_url(href)
            if handle:
                return handle
        
        # Method 2: Look for Instagram in social media sections
        # Common patterns: class="social", id="social", class="footer-social", etc.
        social_sections = soup.find_all(['div', 'nav', 'footer', 'section'], 
                                       class_=re.compile(r'social|footer|contact', re.IGNORECASE))
        for section in social_sections:
            links = section.find_all('a', href=re.compile(r'instagram\.com', re.IGNORECASE))
            for link in links:
                href = link.get('href', '')
                handle = _extract_instagram_handle_from_url(href)
                if handle:
                    return handle
        
        # Method 3: Search entire page content for Instagram URLs
        page_text = soup.get_text()
        instagram_pattern = r'instagram\.com/([a-zA-Z0-9._]+)'
        matches = re.findall(instagram_pattern, page_text, re.IGNORECASE)
        if matches:
            # Return the first valid handle
            for match in matches:
                if match and match not in ['p', 'reel', 'tv', 'stories', 'explore']:
                    return match
        
        # Method 4: Check meta tags
        meta_tags = soup.find_all('meta', property=re.compile(r'og:|twitter:', re.IGNORECASE))
        for meta in meta_tags:
            content = meta.get('content', '')
            if 'instagram.com' in content.lower():
                handle = _extract_instagram_handle_from_url(content)
                if handle:
                    return handle
        
        return None
    
    except requests.RequestException as e:
        print(f"Error fetching website {website_url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error parsing website {website_url}: {str(e)}")
        return None


def _extract_instagram_handle_from_url(url: str) -> Optional[str]:
    """
    Extracts Instagram handle from an Instagram URL.
    
    Args:
        url: Instagram URL or link
    
    Returns:
        Instagram handle without @, or None if invalid
    """
    if not url:
        return None
    
    # Pattern to match Instagram URLs
    # Examples: 
    # - https://www.instagram.com/username/
    # - https://instagram.com/username
    # - instagram.com/username/
    pattern = r'instagram\.com/([a-zA-Z0-9._]+)'
    match = re.search(pattern, url, re.IGNORECASE)
    
    if match:
        handle = match.group(1).rstrip('/')
        
        # Filter out Instagram system paths
        if handle.lower() not in ['p', 'reel', 'tv', 'stories', 'explore', 'accounts', 'direct']:
            return handle
    
    return None




