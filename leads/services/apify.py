"""
Apify API integration for TikTok and Instagram scraping.

IMPORTANT: 
- TikTok/Instagram scraping via Apify must respect the platforms' Terms of Service.
- This is for R&D and internal research purposes only.
- We DO NOT implement any automated messaging/DM functionality.
- We only discover and store public profile information for lead generation.

Requires the following environment variables:
- APIFY_TOKEN: Your Apify API token
- APIFY_ACTOR_TIKTOK: Actor ID for TikTok search
- APIFY_ACTOR_INSTAGRAM: Actor ID for Instagram search
"""

import requests
import time
import re
from django.conf import settings
from typing import List, Dict, Optional


def run_apify_actor(query: str, platform: str, search_type: str = 'profile') -> List[Dict]:
    """
    Calls Apify actor and returns a normalized list of accounts/leads.
    
    Args:
        query: Search query string (e.g., "starbucks" for profile, "Tokyo" for place)
        platform: Either "tiktok" or "instagram"
        search_type: Type of search - "profile", "hashtag", or "place"
    
    Returns:
        List of dictionaries containing account information:
        - name: Account/business name
        - username: Username/handle (without @ symbol)
        - profile_url: Full URL to profile
        - platform: "tiktok" or "instagram"
        - follower_count: Number of followers (if available)
        - bio: Profile bio/description (if available)
        - location: Location name (if searching by place)
    
    Raises:
        ValueError: If configuration is missing or platform is invalid
        Exception: If API call fails
    """
    api_token = settings.APIFY_TOKEN
    
    if not api_token:
        raise ValueError("APIFY_TOKEN not configured in settings")
    
    # Get the appropriate actor ID based on platform
    if platform.lower() == 'tiktok':
        actor_id = settings.APIFY_ACTOR_TIKTOK
    elif platform.lower() == 'instagram':
        actor_id = settings.APIFY_ACTOR_INSTAGRAM
    else:
        raise ValueError(f"Invalid platform: {platform}. Must be 'tiktok' or 'instagram'")
    
    if not actor_id:
        raise ValueError(f"APIFY_ACTOR_{platform.upper()} not configured in settings")
    
    # Start the actor run
    run_id = _start_actor_run(actor_id, query, api_token, search_type, platform)
    
    # Wait for the run to complete
    results = _wait_for_run_completion(run_id, api_token)
    
    # Normalize the results based on platform
    normalized = _normalize_results(results, platform.lower())
    
    return normalized


def _start_actor_run(actor_id: str, query: str, api_token: str, search_type: str = 'profile', platform: str = 'instagram') -> str:
    """
    Starts an Apify actor run.
    
    Args:
        actor_id: The Apify actor ID
        query: The search query
        api_token: Apify API token
        search_type: Type of search - "profile", "hashtag", or "place"
        platform: Platform being searched - "tiktok" or "instagram"
    
    Returns:
        Run ID for the started actor
    """
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}',
    }
    
    # Build payload based on search type and platform
    # Each actor has specific input requirements
    
    if platform.lower() == 'tiktok':
        # TikTok actors
        if search_type == 'profile':
            profiles = [p.strip() for p in query.replace(',', ' ').split() if p.strip()]
            payload = {
                'profiles': profiles,
                'resultsLimit': 20,
            }
        elif search_type == 'hashtag':
            hashtag = query.strip().lstrip('#')
            payload = {
                'hashtags': [hashtag],
                'resultsPerPage': 20,
            }
        else:
            payload = {
                'search': query.strip(),
                'resultsLimit': 20,
            }
    
    else:  # Instagram
        # Instagram Search Scraper (apify/instagram-search-scraper)
        # This actor supports: user, hashtag, place search types
        
        if search_type == 'profile':
            # For profile/user search
            # Can accept multiple usernames separated by space
            usernames = [u.strip() for u in query.replace(',', ' ').split() if u.strip()]
            
            # Instagram Search Scraper uses 'search' field with searchType
            payload = {
                'search': ' '.join(usernames),
                'searchType': 'user',
                'resultsLimit': 20,
            }
        
        elif search_type == 'hashtag':
            # For hashtag search
            hashtag = query.strip().lstrip('#')
            payload = {
                'search': hashtag,
                'searchType': 'hashtag',
                'resultsLimit': 20,
            }
        
        elif search_type == 'place':
            # For place/location search
            payload = {
                'search': query.strip(),
                'searchType': 'place',
                'resultsLimit': 20,
            }
        
        else:
            # Fallback
            payload = {
                'search': query.strip(),
                'searchType': 'user',
                'resultsLimit': 20,
            }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        run_id = data.get('data', {}).get('id')
        if not run_id:
            raise Exception("Failed to get run ID from Apify response")
        
        return run_id
    
    except requests.RequestException as e:
        # Include more details about the error
        error_msg = f"Failed to start Apify actor: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                error_msg += f"\nAPI Response: {error_details}"
            except:
                error_msg += f"\nAPI Response: {e.response.text}"
        raise Exception(error_msg)


def _wait_for_run_completion(run_id: str, api_token: str, max_wait_seconds: int = 300) -> List[Dict]:
    """
    Polls the Apify API until the run completes.
    
    Args:
        run_id: The actor run ID
        api_token: Apify API token
        max_wait_seconds: Maximum time to wait (default: 5 minutes)
    
    Returns:
        List of results from the actor run
    """
    url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    
    start_time = time.time()
    
    while True:
        if time.time() - start_time > max_wait_seconds:
            raise Exception("Apify actor run timed out")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            status = data.get('data', {}).get('status')
            
            if status == 'SUCCEEDED':
                # Fetch the dataset results
                return _fetch_dataset_items(run_id, api_token)
            
            elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                raise Exception(f"Apify actor run {status.lower()}")
            
            # Still running, wait and retry
            time.sleep(5)
        
        except requests.RequestException as e:
            raise Exception(f"Failed to check Apify run status: {str(e)}")


def _fetch_dataset_items(run_id: str, api_token: str) -> List[Dict]:
    """
    Fetches the dataset items from a completed actor run.
    """
    url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch Apify dataset items: {str(e)}")


def _extract_instagram_handle(bio_text: str) -> Optional[str]:
    """
    Extracts Instagram handle from TikTok bio text.
    
    Looks for patterns like:
    - IG: @username
    - Instagram: username
    - @username (assuming it's Instagram if mentioned with IG/Insta)
    - instagram.com/username
    
    Returns:
        Instagram handle without @ symbol, or None if not found
    """
    if not bio_text:
        return None
    
    # Pattern 1: Direct Instagram URL
    url_pattern = r'instagram\.com/([a-zA-Z0-9._]+)'
    match = re.search(url_pattern, bio_text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 2: IG: @username or Instagram: @username
    ig_pattern = r'(?:ig|insta|instagram)[\s:]*@?([a-zA-Z0-9._]+)'
    match = re.search(ig_pattern, bio_text, re.IGNORECASE)
    if match:
        username = match.group(1)
        # Filter out common words that aren't usernames
        if username.lower() not in ['follow', 'me', 'on', 'for', 'more']:
            return username
    
    # Pattern 3: Look for @username after words like "IG" or "Instagram"
    mention_pattern = r'(?:ig|insta|instagram)[\s:]*[@]([a-zA-Z0-9._]+)'
    match = re.search(mention_pattern, bio_text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Pattern 4: Find Instagram handle in emoji context (common in bios)
    # e.g., "📷 @username" or "IG 📸 username"
    emoji_pattern = r'(?:📷|📸|💌)[\s]*@?([a-zA-Z0-9._]{3,30})'
    match = re.search(emoji_pattern, bio_text)
    if match and ('ig' in bio_text.lower() or 'insta' in bio_text.lower()):
        return match.group(1)
    
    return None


def _normalize_results(results: List[Dict], platform: str) -> List[Dict]:
    """
    Normalizes results from different Apify actors into a consistent format.
    
    Note: Field names may vary depending on the specific Apify actor you use.
    Adjust the field mappings below based on your actor's output schema.
    """
    normalized = []
    
    for item in results:
        # Common field mappings - adjust based on your specific Apify actors
        if platform == 'tiktok':
            bio = item.get('authorMeta', {}).get('signature', '') or item.get('signature', '')
            
            # Extract Instagram handle from bio
            instagram_handle = _extract_instagram_handle(bio)
            
            normalized_item = {
                'name': item.get('authorMeta', {}).get('name') or item.get('nickname', ''),
                'username': item.get('authorMeta', {}).get('name') or item.get('author', ''),
                'profile_url': f"https://www.tiktok.com/@{item.get('author', '')}",
                'platform': 'tiktok',
                'follower_count': item.get('authorMeta', {}).get('fans', 0),
                'bio': bio,
                'instagram_handle': instagram_handle,  # Add extracted Instagram handle
                'instagram_url': f"https://www.instagram.com/{instagram_handle}/" if instagram_handle else None,
            }
        
        elif platform == 'instagram':
            username = item.get('username', '')
            normalized_item = {
                'name': item.get('full_name') or item.get('fullName', ''),
                'username': username,
                'profile_url': f"https://www.instagram.com/{username}/",
                'platform': 'instagram',
                'follower_count': item.get('followersCount') or item.get('edge_followed_by', {}).get('count', 0),
                'bio': item.get('biography', ''),
            }
        
        else:
            continue
        
        # Only add if we have at least a username
        if normalized_item.get('username'):
            normalized.append(normalized_item)
    
    return normalized




