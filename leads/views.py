from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.conf import settings

from .models import Cafe, SearchQuery
from .forms import GoogleMapsSearchForm, ApifySearchForm, CafeUpdateForm, CafeFilterForm
from .services.google_maps import search_places, get_place_details, extract_instagram_from_website
from .services.apify import run_apify_actor
from .services.google_sheets import export_cafes_to_sheet, append_cafes_to_sheet, export_to_new_tab


def auto_export_to_sheets(cafe):
    """
    Automatically append a single café to Google Sheets.
    Called whenever a new café is saved.
    """
    # Check if auto-export is enabled
    if not getattr(settings, 'GOOGLE_SHEETS_AUTO_EXPORT', True):
        return
    
    try:
        spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID
        
        if not spreadsheet_id:
            return  # Silently skip if not configured
        
        cafe_data = [{
            'name': cafe.name,
            'city': cafe.city or '',
            'address': cafe.address or '',
            'website': cafe.website or '',
            'instagram_handle': cafe.instagram_handle or '',
            'tiktok_handle': cafe.tiktok_handle or '',
            'source': cafe.source,
            'created_at': cafe.created_at,
            'notes': cafe.notes or ''
        }]
        
        # Append to existing sheet (doesn't clear data)
        append_cafes_to_sheet(
            cafe_data, 
            spreadsheet_id,
            sheet_name=getattr(settings, 'GOOGLE_SHEETS_SHEET_NAME', 'Sheet1')
        )
        
    except Exception as e:
        # Log error but don't break the save process
        print(f"Auto-export to Google Sheets failed: {str(e)}")
        pass


# ============================================================================
# Authentication Views
# ============================================================================

# Signup disabled - accounts created via admin panel only
# def signup_view(request):
#     """
#     User registration view - DISABLED.
#     Create users via Django admin panel instead.
#     """
#     pass


def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ============================================================================
# Dashboard View
# ============================================================================

@login_required
def dashboard_view(request):
    """
    Main dashboard showing statistics and recent cafés.
    """
    # Total cafés count
    total_cafes = Cafe.objects.count()
    
    # Count by source
    source_stats = Cafe.objects.values('source').annotate(count=Count('id')).order_by('-count')
    
    # Latest 10 cafés
    latest_cafes = Cafe.objects.all()[:10]
    
    # Recent search queries
    recent_searches = SearchQuery.objects.filter(created_by=request.user)[:5]
    
    context = {
        'total_cafes': total_cafes,
        'source_stats': source_stats,
        'latest_cafes': latest_cafes,
        'recent_searches': recent_searches,
    }
    
    return render(request, 'leads/dashboard.html', context)


# ============================================================================
# Google Maps Search Views
# ============================================================================

@login_required
def google_search_view(request):
    """
    Google Maps search page - handles search and displays results.
    """
    form = GoogleMapsSearchForm()
    results = None
    error = None
    
    if request.method == 'POST':
        if 'search' in request.POST:
            # Handle search form submission
            form = GoogleMapsSearchForm(request.POST)
            if form.is_valid():
                query = form.cleaned_data['query']
                
                try:
                    # Search using Google Maps API
                    results = search_places(query)
                    
                    # Enhance results with website information and Instagram
                    for result in results:
                        if result.get('place_id'):
                            details = get_place_details(result['place_id'])
                            if details and details.get('website'):
                                result['website'] = details['website']
                                
                                # Extract Instagram handle from website
                                instagram_handle = extract_instagram_from_website(details['website'])
                                if instagram_handle:
                                    result['instagram_handle'] = instagram_handle
                                    result['instagram_url'] = f"https://www.instagram.com/{instagram_handle}/"
                    
                    # Store results in session for display
                    request.session['google_search_results'] = results
                    request.session['google_search_query'] = query
                    
                    messages.success(request, f'Found {len(results)} results for "{query}"')
                    
                    # AUTO-SAVE cafés with Instagram handles immediately
                    saved_cafes = []
                    saved_count = 0
                    
                    for result in results:
                        # Only save if Instagram handle was found
                        if not result.get('instagram_handle'):
                            continue
                            
                        # Check if café already exists by place_id
                        if result.get('place_id'):
                            existing = Cafe.objects.filter(google_place_id=result['place_id']).first()
                            if existing:
                                continue
                        
                        # Create new café entry
                        cafe = Cafe.objects.create(
                            name=result.get('name', ''),
                            city=result.get('city', ''),
                            address=result.get('address', ''),
                            website=result.get('website', ''),
                            instagram_handle=result.get('instagram_handle', ''),
                            source='google_maps',
                            google_place_id=result.get('place_id', ''),
                        )
                        saved_count += 1
                        
                        # Add to list for bulk export
                        saved_cafes.append({
                            'name': cafe.name,
                            'city': cafe.city or '',
                            'address': cafe.address or '',
                            'website': cafe.website or '',
                            'instagram_handle': cafe.instagram_handle or '',
                            'tiktok_handle': '',
                            'source': cafe.source,
                            'created_at': cafe.created_at,
                            'notes': cafe.notes or ''
                        })
                    
                    # Export to NEW TAB in Google Sheets if any cafés with Instagram were found
                    if saved_cafes and settings.GOOGLE_SHEETS_SPREADSHEET_ID:
                        try:
                            print(f"DEBUG: Auto-saving {len(saved_cafes)} cafés with Instagram to Google Sheets")
                            export_result = export_to_new_tab(
                                saved_cafes,
                                settings.GOOGLE_SHEETS_SPREADSHEET_ID,
                                search_query=query,
                                source='Google Maps'
                            )
                            messages.success(
                                request,
                                f'Auto-saved {saved_count} café(s) with Instagram! '
                                f'Exported to: <strong>{export_result["tab_name"]}</strong>. '
                                f'<a href="{export_result["spreadsheet_url"]}" target="_blank" class="alert-link">Open Sheet</a>',
                                extra_tags='safe'
                            )
                        except Exception as e:
                            print(f"DEBUG: Export failed: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            if saved_count > 0:
                                messages.warning(request, f'Saved {saved_count} café(s) with Instagram but export failed: {str(e)}')
                    elif saved_count > 0:
                        messages.success(request, f'Auto-saved {saved_count} café(s) with Instagram!')
                    elif len(results) > 0:
                        messages.info(request, f'Found {len(results)} cafés but none had Instagram links.')
                
                except Exception as e:
                    error = str(e)
                    messages.error(request, f'Search failed: {error}')
    
    # If we have results in session, display them
    if not results and 'google_search_results' in request.session:
        results = request.session['google_search_results']
    
    context = {
        'form': form,
        'results': results,
        'error': error,
    }
    
    return render(request, 'leads/google_search.html', context)


# ============================================================================
# Apify Search Views
# ============================================================================

@login_required
def apify_search_view(request):
    """
    Apify search page for TikTok/Instagram - handles search and displays results.
    Supports profile, hashtag, and place searches.
    """
    form = ApifySearchForm()
    results = None
    error = None
    
    if request.method == 'POST':
        if 'search' in request.POST:
            # Handle search form submission
            form = ApifySearchForm(request.POST)
            if form.is_valid():
                query = form.cleaned_data['query']
                platform = form.cleaned_data['platform']
                search_type = form.cleaned_data.get('search_type', 'profile')
                
                # Create search query record with 'running' status
                search_query = SearchQuery.objects.create(
                    query_text=f"{search_type}: {query}",
                    platform=platform,
                    status='running',
                    created_by=request.user,
                )
                
                try:
                    # Run Apify actor with search type
                    results = run_apify_actor(query, platform, search_type)
                    
                    # Store results in session for display
                    request.session['apify_search_results'] = results
                    request.session['apify_search_query'] = query
                    request.session['apify_search_platform'] = platform
                    request.session['apify_search_type'] = search_type
                    request.session['apify_search_query_id'] = search_query.id
                    
                    # Update search query status to 'done'
                    search_query.status = 'done'
                    search_query.save()
                    
                    messages.success(request, f'Found {len(results)} results for "{query}" on {platform} ({search_type})')
                    
                    # AUTO-SAVE all results with Instagram immediately
                    source_mapping = {
                        'tiktok': 'apify_tiktok',
                        'instagram': 'apify_instagram',
                    }
                    source = source_mapping.get(platform, 'manual')
                    
                    saved_cafes = []
                    saved_count = 0
                    
                    for result in results:
                        username = result.get('username', '')
                        
                        if not username:
                            continue
                        
                        # For TikTok, only save if Instagram handle was extracted from bio
                        # For Instagram, save all results
                        if platform == 'tiktok' and not result.get('instagram_handle'):
                            continue
                        
                        # Check if café already exists by handle
                        field_name = f'{platform}_handle'
                        filter_kwargs = {field_name: username}
                        existing = Cafe.objects.filter(**filter_kwargs).first()
                        
                        if existing:
                            continue
                        
                        # Create new café entry
                        cafe_data = {
                            'name': result.get('name', username),
                            'source': source,
                        }
                        
                        # Add location if available (from place search)
                        if result.get('location'):
                            cafe_data['city'] = result.get('location', '')
                        
                        if platform == 'tiktok':
                            cafe_data['tiktok_handle'] = username
                            # If Instagram handle was extracted from TikTok bio, save it too
                            if result.get('instagram_handle'):
                                cafe_data['instagram_handle'] = result.get('instagram_handle')
                        elif platform == 'instagram':
                            cafe_data['instagram_handle'] = username
                        
                        cafe = Cafe.objects.create(**cafe_data)
                        saved_count += 1
                        
                        # Add to list for bulk export
                        saved_cafes.append({
                            'name': cafe.name,
                            'city': cafe.city or '',
                            'address': cafe.address or '',
                            'website': cafe.website or '',
                            'instagram_handle': cafe.instagram_handle or '',
                            'tiktok_handle': cafe.tiktok_handle or '',
                            'source': cafe.source,
                            'created_at': cafe.created_at,
                            'notes': cafe.notes or ''
                        })
                    
                    # Export to NEW TAB in Google Sheets
                    if saved_cafes and settings.GOOGLE_SHEETS_SPREADSHEET_ID:
                        try:
                            platform_name = platform.title()
                            print(f"DEBUG APIFY: Auto-saving {len(saved_cafes)} accounts to Google Sheets")
                            export_result = export_to_new_tab(
                                saved_cafes,
                                settings.GOOGLE_SHEETS_SPREADSHEET_ID,
                                search_query=query,
                                source=platform_name
                            )
                            messages.success(
                                request,
                                f'Auto-saved {saved_count} account(s) with Instagram! '
                                f'Exported to: <strong>{export_result["tab_name"]}</strong>. '
                                f'<a href="{export_result["spreadsheet_url"]}" target="_blank" class="alert-link">Open Sheet</a>',
                                extra_tags='safe'
                            )
                        except Exception as e:
                            print(f"DEBUG APIFY: Export failed: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            if saved_count > 0:
                                messages.warning(request, f'Saved {saved_count} accounts but export failed: {str(e)}')
                    elif saved_count > 0:
                        messages.success(request, f'Auto-saved {saved_count} account(s) with Instagram!')
                    elif platform == 'tiktok':
                        messages.info(request, f'Found {len(results)} TikTok accounts but none had Instagram in bio.')
                
                except Exception as e:
                    error = str(e)
                    search_query.status = 'failed'
                    search_query.save()
                    messages.error(request, f'Search failed: {error}')
    
    # If we have results in session, display them
    if not results and 'apify_search_results' in request.session:
        results = request.session['apify_search_results']
    
    context = {
        'form': form,
        'results': results,
        'error': error,
    }
    
    return render(request, 'leads/apify_search.html', context)


# ============================================================================
# Café List and Detail Views
# ============================================================================

@login_required
def cafe_list_view(request):
    """
    Paginated list of all cafés with filtering and export functionality.
    """
    # Get all cafés
    cafes = Cafe.objects.all()
    
    # Handle filters
    filter_form = CafeFilterForm(request.GET)
    if filter_form.is_valid():
        source = filter_form.cleaned_data.get('source')
        city = filter_form.cleaned_data.get('city')
        
        if source:
            cafes = cafes.filter(source=source)
        
        if city:
            cafes = cafes.filter(city__icontains=city)
    
    # Handle export to Google Sheets
    if request.method == 'POST' and 'export_to_sheets' in request.POST:
        try:
            # Get predefined spreadsheet ID from settings
            spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID
            
            if not spreadsheet_id:
                messages.error(
                    request,
                    'Google Sheets spreadsheet not configured. Please add GOOGLE_SHEETS_SPREADSHEET_ID to your .env file. '
                    'See GOOGLE_SHEETS_SETUP.md for instructions.'
                )
                return redirect('cafe_list')
            
            # Prepare café data for export
            cafes_data = []
            for cafe in cafes:
                cafes_data.append({
                    'name': cafe.name,
                    'city': cafe.city or '',
                    'address': cafe.address or '',
                    'website': cafe.website or '',
                    'instagram_handle': cafe.instagram_handle or '',
                    'tiktok_handle': cafe.tiktok_handle or '',
                    'source': cafe.source,
                    'created_at': cafe.created_at,
                    'notes': cafe.notes or ''
                })
            
            # Export to predefined Google Sheet
            result = export_cafes_to_sheet(
                cafes_data, 
                spreadsheet_id=spreadsheet_id,
                sheet_name=getattr(settings, 'GOOGLE_SHEETS_SHEET_NAME', 'Sheet1')
            )
            
            messages.success(
                request,
                f'Successfully exported {result["rows_exported"]} cafés to Google Sheets! '
                f'<a href="{result["spreadsheet_url"]}" target="_blank" class="alert-link">Open Spreadsheet</a>',
                extra_tags='safe'
            )
            
            # Store spreadsheet URL in session for quick access
            request.session['spreadsheet_url'] = result['spreadsheet_url']
        
        except FileNotFoundError as e:
            messages.error(
                request,
                'Google Sheets credentials not found. Please follow the setup instructions in GOOGLE_SHEETS_SETUP.md'
            )
        except Exception as e:
            messages.error(request, f'Export failed: {str(e)}')
        
        return redirect('cafe_list')
    
    # Pagination
    paginator = Paginator(cafes, 20)  # Show 20 cafés per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_cafes': cafes.count(),
        'spreadsheet_url': request.session.get('spreadsheet_url'),
        'spreadsheet_id': settings.GOOGLE_SHEETS_SPREADSHEET_ID,
    }
    
    return render(request, 'leads/cafe_list.html', context)


class CafeDetailView(LoginRequiredMixin, DetailView):
    """
    Detailed view of a single café.
    """
    model = Cafe
    template_name = 'leads/cafe_detail.html'
    context_object_name = 'cafe'


class CafeUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for editing café information.
    """
    model = Cafe
    form_class = CafeUpdateForm
    template_name = 'leads/cafe_update.html'
    
    def get_success_url(self):
        messages.success(self.request, 'Café updated successfully!')
        return reverse_lazy('cafe_detail', kwargs={'pk': self.object.pk})




