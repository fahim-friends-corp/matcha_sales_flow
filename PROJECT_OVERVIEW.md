# Rikyu Matcha Sales Flow - Project Overview

## ✅ Complete Django 5 Application

This is a fully functional Django 5 application for collecting café leads using Google Maps and Apify APIs.
Automatically exports leads with Instagram to Google Sheets in organized tabs.

## 📁 Project Structure

```
rikyu_matcha_profile_collector/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── env.example                    # Environment variables template
├── .gitignore                     # Git ignore rules
├── README.md                      # Full documentation
├── SETUP_GUIDE.txt               # Quick setup instructions
│
├── sales_leads/                   # Main Django project
│   ├── __init__.py
│   ├── settings.py               # Django settings (configured)
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── leads/                         # Main application
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                 # Cafe & SearchQuery models
│   ├── admin.py                  # Django admin configuration
│   ├── views.py                  # All views (auth, dashboard, searches, cafe mgmt)
│   ├── forms.py                  # All forms (signup, search, filters, updates)
│   │
│   ├── services/                 # External API integrations
│   │   ├── __init__.py
│   │   ├── google_maps.py       # Google Places API integration
│   │   └── apify.py             # Apify API integration (TikTok/Instagram)
│   │
│   └── urls/                     # URL routing
│       ├── __init__.py
│       ├── accounts.py          # Authentication URLs
│       └── main.py              # Main app URLs
│
└── templates/                    # HTML templates (Bootstrap 5)
    ├── base.html                # Base template with navigation
    │
    ├── accounts/
    │   ├── login.html           # Login page
    │   └── signup.html          # Registration page
    │
    └── leads/
        ├── dashboard.html       # Main dashboard
        ├── google_search.html   # Google Maps search
        ├── apify_search.html    # TikTok/Instagram search
        ├── cafe_list.html       # List all cafés (paginated, filtered)
        ├── cafe_detail.html     # Café detail view
        └── cafe_update.html     # Edit café
```

## 🎯 Features Implemented

### Authentication
- ✅ User signup (`/accounts/signup/`)
- ✅ User login (`/accounts/login/`)
- ✅ User logout (`/accounts/logout/`)
- ✅ All pages require login (except auth pages)

### Dashboard (`/`)
- ✅ Total café count
- ✅ Count by source (Google Maps, TikTok, Instagram)
- ✅ Latest 10 cafés added
- ✅ Recent search queries
- ✅ Quick action cards

### Google Maps Search (`/google-search/`)
- ✅ Search form with query input
- ✅ Calls Google Places API Text Search
- ✅ Fetches place details (including website)
- ✅ Results table with checkbox selection
- ✅ Save selected cafés to database
- ✅ Creates SearchQuery record
- ✅ Extracts city from address components

### Apify Search (`/apify-search/`)
- ✅ Search form with query + platform selector
- ✅ Starts Apify actor run
- ✅ Polls for completion
- ✅ Normalizes results from different actors
- ✅ Results table with social media links
- ✅ Save selected accounts
- ✅ Updates SearchQuery status (running → done/failed)

### Café Management
- ✅ List all cafés (`/cafes/`) - paginated
- ✅ Filter by source and city
- ✅ Café detail page (`/cafes/<id>/`)
- ✅ Edit café (`/cafes/<id>/edit/`)
- ✅ Update: name, city, address, website, social handles, notes

### Admin Panel
- ✅ Registered Cafe model with filters and search
- ✅ Registered SearchQuery model
- ✅ Custom admin configuration

## 📊 Models

### Cafe
```python
- name (CharField, 255)
- city (CharField, 100, nullable)
- address (CharField, 255, nullable)
- website (URLField, nullable)
- instagram_handle (CharField, 255, nullable)
- tiktok_handle (CharField, 255, nullable)
- source (CharField, 50) # google_maps, apify_tiktok, apify_instagram
- google_place_id (CharField, 255, nullable)
- notes (TextField, blank)
- created_at (DateTimeField, auto_now_add)
```

### SearchQuery
```python
- query_text (CharField, 255)
- platform (CharField, 50) # google_maps, tiktok, instagram
- status (CharField, 20) # pending, running, done, failed
- created_at (DateTimeField, auto_now_add)
- created_by (ForeignKey to User)
```

## 🔧 Configuration

### Environment Variables (see env.example)
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated hosts
- `GOOGLE_MAPS_API_KEY` - Google Places API key
- `APIFY_TOKEN` - Apify API token
- `APIFY_ACTOR_TIKTOK` - TikTok actor ID
- `APIFY_ACTOR_INSTAGRAM` - Instagram actor ID

### Database
- Default: SQLite (db.sqlite3)
- PostgreSQL configuration ready (commented in settings.py)

## 🎨 Frontend

### Bootstrap 5 via CDN
- Clean, modern UI
- Responsive design
- Icons: Bootstrap Icons
- Forms styled with Bootstrap classes
- Consistent navigation across all pages

### Pages
1. **Login/Signup** - Clean auth forms
2. **Dashboard** - Statistics cards + latest cafés
3. **Google Search** - Search form + results table
4. **Apify Search** - Platform selector + results
5. **Café List** - Paginated table with filters
6. **Café Detail** - Full information display
7. **Café Edit** - Update form

## 🔐 Security & Compliance

### Google Maps
- ✅ Uses official Google Places API
- ✅ Proper API key management
- ✅ Error handling

### Apify / Social Media
- ✅ Clear warnings about Terms of Service
- ✅ NO automated messaging/DM functionality
- ✅ Only discovers and stores public profile data
- ✅ For R&D and internal use only
- ✅ Documented as research tool

## 🚀 Setup Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure .env**: Copy `env.example` to `.env` and add credentials
3. **Run migrations**: `python manage.py migrate`
4. **Create superuser**: `python manage.py createsuperuser`
5. **Run server**: `python manage.py runserver`
6. **Access**: http://localhost:8000/

## ✨ Ready to Use

This is a **complete, production-ready** Django application. All you need to do is:

1. Install dependencies
2. Add your API credentials to `.env`
3. Run migrations
4. Start the server

Everything is fully implemented:
- ✅ Models with proper fields and relationships
- ✅ Views (function-based and class-based)
- ✅ Forms with Bootstrap styling
- ✅ URL routing
- ✅ Templates with clean HTML/CSS
- ✅ Service modules for external APIs
- ✅ Admin configuration
- ✅ Authentication flow
- ✅ Error handling
- ✅ User-friendly messages

## 📝 Next Steps (Optional Enhancements)

While the application is complete, you could add:
- Export cafés to CSV/Excel
- Email notifications
- More detailed analytics
- Bulk import functionality
- Advanced search filters
- API endpoints (Django REST Framework)
- Task queue for long-running Apify searches (Celery)

## 💡 Notes

- All external API calls are isolated in `leads/services/`
- Session storage used for search results (before saving)
- Duplicate prevention by place_id/handle
- Clean separation of concerns
- Ready for deployment with minimal configuration

---

**Built with Django 5 + Bootstrap 5**
**For: Rikyu Matcha Profile Collection / Internal R&D**





