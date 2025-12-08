#!/usr/bin/env python
"""
Test script to verify Apify actor configuration.
Run this before using the Django app to ensure your actors work.

Usage:
    python test_apify.py
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_apify_actor(actor_id, platform_name):
    """Test if an Apify actor is accessible and valid."""
    print(f"\n{'='*60}")
    print(f"Testing {platform_name} Actor: {actor_id}")
    print('='*60)
    
    api_token = os.getenv('APIFY_TOKEN')
    
    if not api_token:
        print("❌ ERROR: APIFY_TOKEN not found in .env file")
        return False
    
    if not actor_id:
        print(f"❌ ERROR: Actor ID for {platform_name} not found in .env file")
        return False
    
    # Test 1: Check if actor exists
    print("\n1. Checking if actor exists...")
    url = f"https://api.apify.com/v2/acts/{actor_id}"
    headers = {'Authorization': f'Bearer {api_token}'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            print(f"❌ Actor not found!")
            print(f"   The actor ID '{actor_id}' does not exist or is not accessible.")
            print(f"   Visit https://apify.com/store to find valid actors.")
            return False
        elif response.status_code == 401:
            print(f"❌ Authentication failed!")
            print(f"   Your APIFY_TOKEN is invalid or expired.")
            return False
        elif response.status_code == 403:
            print(f"❌ Access denied!")
            print(f"   You don't have permission to access this actor.")
            return False
        
        response.raise_for_status()
        actor_data = response.json()
        
        print(f"✅ Actor found!")
        print(f"   Name: {actor_data.get('data', {}).get('name', 'N/A')}")
        print(f"   Username: {actor_data.get('data', {}).get('username', 'N/A')}")
        print(f"   Title: {actor_data.get('data', {}).get('title', 'N/A')}")
        
    except requests.RequestException as e:
        print(f"❌ Error checking actor: {str(e)}")
        return False
    
    # Test 2: Check actor input schema
    print("\n2. Checking actor input schema...")
    input_url = f"https://api.apify.com/v2/acts/{actor_id}/input-schema"
    
    try:
        response = requests.get(input_url, headers=headers, timeout=10)
        if response.status_code == 200:
            schema = response.json()
            print(f"✅ Input schema available")
            
            # Show required properties if available
            properties = schema.get('properties', {})
            if properties:
                print(f"\n   Available input fields:")
                for field_name, field_info in list(properties.items())[:5]:
                    required = "required" if field_name in schema.get('required', []) else "optional"
                    print(f"   - {field_name} ({required})")
                if len(properties) > 5:
                    print(f"   ... and {len(properties) - 5} more fields")
        else:
            print(f"⚠️  Could not fetch input schema (status {response.status_code})")
    except requests.RequestException as e:
        print(f"⚠️  Could not fetch input schema: {str(e)}")
    
    # Test 3: Try to start a test run (optional - costs credits!)
    print("\n3. Testing actor execution...")
    print("⚠️  Skipping execution test to save credits.")
    print("   To test execution, uncomment the test in test_apify.py")
    
    # Uncomment to actually test running the actor (will cost Apify credits!)
    # test_payload = {
    #     'search': 'test',
    #     'maxResults': 1,
    # }
    # run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
    # try:
    #     response = requests.post(run_url, json=test_payload, headers={
    #         'Content-Type': 'application/json',
    #         'Authorization': f'Bearer {api_token}',
    #     }, timeout=30)
    #     
    #     if response.status_code == 201:
    #         print(f"✅ Successfully started test run")
    #     else:
    #         print(f"❌ Failed to start run: {response.status_code}")
    #         print(f"   Response: {response.text}")
    # except requests.RequestException as e:
    #     print(f"❌ Error starting run: {str(e)}")
    
    return True


def main():
    print("\n" + "="*60)
    print("Apify Actor Configuration Test")
    print("="*60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n❌ ERROR: .env file not found!")
        print("   Create a .env file based on env.example")
        return
    
    # Test TikTok actor
    tiktok_actor = os.getenv('APIFY_ACTOR_TIKTOK')
    tiktok_ok = test_apify_actor(tiktok_actor, 'TikTok')
    
    # Test Instagram actor
    instagram_actor = os.getenv('APIFY_ACTOR_INSTAGRAM')
    instagram_ok = test_apify_actor(instagram_actor, 'Instagram')
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if tiktok_ok and instagram_ok:
        print("✅ All actors are configured correctly!")
        print("\nYou can now use the Apify search feature in the Django app.")
    else:
        print("❌ Some actors have configuration issues.")
        print("\nPlease fix the issues above and run this test again.")
        print("\nFor help, see: APIFY_SETUP_GUIDE.md")
    
    print("\n")


if __name__ == '__main__':
    main()
