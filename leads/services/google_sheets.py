"""
Google Sheets integration for exporting café leads.

This module provides functions to export café data to Google Sheets.
Requires Google Sheets API credentials to be configured.
"""

import os
import datetime
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings


# Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def get_sheets_service():
    """
    Creates and returns a Google Sheets API service instance.
    
    Returns:
        Google Sheets API service object
    
    Raises:
        FileNotFoundError: If credentials file is not found
        Exception: If authentication fails
    """
    # Path to service account credentials JSON file
    credentials_path = getattr(settings, 'GOOGLE_SHEETS_CREDENTIALS_PATH', None)
    
    if not credentials_path:
        credentials_path = os.path.join(settings.BASE_DIR, 'credentials', 'google_sheets_credentials.json')
    
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"Google Sheets credentials not found at: {credentials_path}\n"
            "Please follow the setup instructions in GOOGLE_SHEETS_SETUP.md"
        )
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        raise Exception(f"Failed to authenticate with Google Sheets: {str(e)}")


def create_new_sheet_tab(spreadsheet_id: str, tab_name: str) -> Dict:
    """
    Creates a new tab/sheet in an existing Google Spreadsheet.
    
    Args:
        spreadsheet_id: The spreadsheet ID
        tab_name: Name for the new tab
    
    Returns:
        Dictionary with sheet_id and sheet_name
    """
    try:
        service = get_sheets_service()
        
        # Create new sheet
        requests = [{
            'addSheet': {
                'properties': {
                    'title': tab_name,
                    'gridProperties': {
                        'frozenRowCount': 1  # Freeze header row
                    }
                }
            }
        }]
        
        body = {
            'requests': requests
        }
        
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        
        # Get the new sheet ID
        sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
        
        return {
            'sheet_id': sheet_id,
            'sheet_name': tab_name,
            'spreadsheet_id': spreadsheet_id
        }
    
    except HttpError as e:
        # If sheet already exists, that's okay
        if 'already exists' in str(e):
            return {
                'sheet_id': None,
                'sheet_name': tab_name,
                'spreadsheet_id': spreadsheet_id,
                'note': 'Sheet already exists'
            }
        raise Exception(f"Failed to create sheet tab: {str(e)}")


def export_to_new_tab(cafes: List[Dict], spreadsheet_id: str, search_query: str = None, source: str = None) -> Dict:
    """
    Creates a new tab and exports cafés to it.
    Tab name is based on search query/source (no timestamp in name, as dates are in rows).
    
    Args:
        cafes: List of café dictionaries
        spreadsheet_id: Spreadsheet ID
        search_query: Optional search query to include in tab name
        source: Source of data (e.g., 'Google Maps', 'TikTok', 'Instagram')
    
    Returns:
        Dictionary with export results and tab information
    """
    try:
        print(f"DEBUG export_to_new_tab: Starting export of {len(cafes)} cafés")
        
        # Generate tab name WITHOUT timestamp (dates are in each row)
        # Add a unique suffix to avoid conflicts
        timestamp_suffix = datetime.datetime.now().strftime('%H%M')  # Just time as suffix
        
        # Create descriptive tab name
        if search_query and source:
            # E.g., "Tokyo - Google Maps (1230)"
            tab_name = f"{search_query[:30]} - {source} ({timestamp_suffix})"
        elif search_query:
            # E.g., "Tokyo cafes (1230)"
            tab_name = f"{search_query[:40]} ({timestamp_suffix})"
        elif source:
            # E.g., "Google Maps (1230)"
            tab_name = f"{source} ({timestamp_suffix})"
        else:
            # E.g., "Export (1230)"
            tab_name = f"Export ({timestamp_suffix})"
        
        # Sanitize tab name (Google Sheets limits)
        tab_name = tab_name[:100]  # Max 100 chars
        
        print(f"DEBUG export_to_new_tab: Tab name: {tab_name}")
        
        # Create new tab
        print(f"DEBUG export_to_new_tab: Creating new tab...")
        tab_result = create_new_sheet_tab(spreadsheet_id, tab_name)
        print(f"DEBUG export_to_new_tab: Tab created: {tab_result}")
        
        # Export data to the new tab
        print(f"DEBUG export_to_new_tab: Exporting data to tab...")
        result = export_cafes_to_sheet(cafes, spreadsheet_id, sheet_name=tab_name)
        print(f"DEBUG export_to_new_tab: Export complete!")
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': result['spreadsheet_url'],
            'tab_name': tab_name,
            'rows_exported': result['rows_exported'],
            'sheet_id': tab_result.get('sheet_id')
        }
    
    except Exception as e:
        print(f"DEBUG export_to_new_tab: ERROR - {str(e)}")
        raise Exception(f"Failed to export to new tab: {str(e)}")
    """
    Creates a new Google Spreadsheet.
    
    Args:
        title: Title for the spreadsheet
    
    Returns:
        Dictionary with spreadsheet_id and spreadsheet_url
    """
    try:
        service = get_sheets_service()
        
        spreadsheet = {
            'properties': {
                'title': title
            },
            'sheets': [{
                'properties': {
                    'title': 'Cafés',
                    'gridProperties': {
                        'frozenRowCount': 1  # Freeze header row
                    }
                }
            }]
        }
        
        result = service.spreadsheets().create(body=spreadsheet).execute()
        
        spreadsheet_id = result['spreadsheetId']
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': spreadsheet_url,
            'title': title
        }
    
    except HttpError as e:
        raise Exception(f"Failed to create spreadsheet: {str(e)}")


def export_cafes_to_sheet(cafes: List[Dict], spreadsheet_id: Optional[str] = None, sheet_name: str = 'Sheet1') -> Dict:
    """
    Exports café data to Google Sheets.
    
    Args:
        cafes: List of café dictionaries with data to export
        spreadsheet_id: Existing spreadsheet ID (creates new if None)
    
    Returns:
        Dictionary with spreadsheet_id and spreadsheet_url
    
    Example:
        cafes = [
            {
                'name': 'Blue Bottle Coffee',
                'city': 'Tokyo',
                'address': '123 Main St',
                'website': 'https://bluebottlecoffee.jp',
                'instagram_handle': 'bluebottlecoffee',
                'tiktok_handle': 'bluebottle',
                'source': 'google_maps',
                'created_at': '2024-01-01'
            }
        ]
    """
    try:
        service = get_sheets_service()
        
        # Create new spreadsheet if not provided
        if not spreadsheet_id:
            result = create_spreadsheet()
            spreadsheet_id = result['spreadsheet_id']
        
        # Prepare header row
        headers = [
            'Name',
            'City',
            'Address',
            'Website',
            'Instagram Handle',
            'Instagram URL',
            'TikTok Handle',
            'TikTok URL',
            'Source',
            'Date Added',
            'Notes'
        ]
        
        # Prepare data rows
        rows = [headers]
        for cafe in cafes:
            instagram_handle = cafe.get('instagram_handle', '')
            tiktok_handle = cafe.get('tiktok_handle', '')
            
            row = [
                cafe.get('name', ''),
                cafe.get('city', ''),
                cafe.get('address', ''),
                cafe.get('website', ''),
                instagram_handle,
                f"https://www.instagram.com/{instagram_handle}/" if instagram_handle else '',
                tiktok_handle,
                f"https://www.tiktok.com/@{tiktok_handle}" if tiktok_handle else '',
                cafe.get('source', '').replace('_', ' ').title(),
                str(cafe.get('created_at', '')),
                cafe.get('notes', '')
            ]
            rows.append(row)
        
        # Clear existing content
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!A:Z'
        ).execute()
        
        # Write data to sheet
        body = {
            'values': rows
        }
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Format header row (bold, background color)
        format_header_row(service, spreadsheet_id)
        
        # Auto-resize columns
        auto_resize_columns(service, spreadsheet_id)
        
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': spreadsheet_url,
            'rows_exported': len(cafes)
        }
    
    except HttpError as e:
        raise Exception(f"Failed to export to Google Sheets: {str(e)}")


def append_cafes_to_sheet(cafes: List[Dict], spreadsheet_id: str, sheet_name: str = 'Sheet1') -> Dict:
    """
    Appends café data to existing Google Sheet (doesn't overwrite).
    
    Args:
        cafes: List of café dictionaries
        spreadsheet_id: ID of existing spreadsheet
    
    Returns:
        Dictionary with update information
    """
    try:
        service = get_sheets_service()
        
        # Prepare data rows (without headers)
        rows = []
        for cafe in cafes:
            instagram_handle = cafe.get('instagram_handle', '')
            tiktok_handle = cafe.get('tiktok_handle', '')
            
            row = [
                cafe.get('name', ''),
                cafe.get('city', ''),
                cafe.get('address', ''),
                cafe.get('website', ''),
                instagram_handle,
                f"https://www.instagram.com/{instagram_handle}/" if instagram_handle else '',
                tiktok_handle,
                f"https://www.tiktok.com/@{tiktok_handle}" if tiktok_handle else '',
                cafe.get('source', '').replace('_', ' ').title(),
                str(cafe.get('created_at', '')),
                cafe.get('notes', '')
            ]
            rows.append(row)
        
        # Append data
        body = {
            'values': rows
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!A:Z',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        
        return {
            'spreadsheet_id': spreadsheet_id,
            'spreadsheet_url': spreadsheet_url,
            'rows_added': len(cafes),
            'updated_range': result.get('updates', {}).get('updatedRange', '')
        }
    
    except HttpError as e:
        raise Exception(f"Failed to append to Google Sheets: {str(e)}")


def format_header_row(service, spreadsheet_id: str):
    """
    Formats the header row (bold, background color).
    """
    try:
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': 0,
                    'startRowIndex': 0,
                    'endRowIndex': 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {
                            'red': 0.2,
                            'green': 0.6,
                            'blue': 0.86
                        },
                        'textFormat': {
                            'bold': True,
                            'foregroundColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            }
                        },
                        'horizontalAlignment': 'CENTER'
                    }
                },
                'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
            }
        }]
        
        body = {
            'requests': requests
        }
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
    
    except HttpError:
        pass  # Non-critical, continue if formatting fails


def auto_resize_columns(service, spreadsheet_id: str):
    """
    Auto-resizes all columns to fit content.
    """
    try:
        requests = [{
            'autoResizeDimensions': {
                'dimensions': {
                    'sheetId': 0,
                    'dimension': 'COLUMNS',
                    'startIndex': 0,
                    'endIndex': 11
                }
            }
        }]
        
        body = {
            'requests': requests
        }
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
    
    except HttpError:
        pass  # Non-critical, continue if resizing fails


def get_or_create_default_spreadsheet() -> str:
    """
    Gets or creates a default spreadsheet for café exports.
    Stores spreadsheet ID in Django settings or database.
    
    Returns:
        Spreadsheet ID
    """
    # You can store this in database or settings
    # For now, create a new one each time
    result = create_spreadsheet("Café Leads - " + str(__import__('datetime').datetime.now().strftime('%Y-%m-%d')))
    return result['spreadsheet_id']
