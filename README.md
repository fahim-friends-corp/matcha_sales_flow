# Rikyu Matcha Sales Flow

An internal Django 5 application for collecting café leads using Google Maps and Apify (TikTok/Instagram scraping).
Auto-exports leads with Instagram handles to Google Sheets.

## Features

- **Google Maps Search**: Search for cafés using Google Places API
- **Social Media Search**: Find café accounts on TikTok and Instagram via Apify
- **Lead Management**: Store, browse, and manage café leads
- **User Authentication**: Django built-in authentication (signup, login, logout)
- **Clean UI**: Bootstrap 5 templates

## Tech Stack

- Python 3.12
- Django 5+
- Bootstrap 5 (via CDN)
- SQLite (default) or PostgreSQL
- Google Places API
- Apify API

## Installation

### 1. Clone or setup the project

```bash
cd /Users/fahimahmed/projects/friends_corp/rikyu_matcha_profile_collector
```

### 2. Create virtual environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
APIFY_TOKEN=your_apify_token
APIFY_ACTOR_TIKTOK=your_tiktok_actor_id
APIFY_ACTOR_INSTAGRAM=your_instagram_actor_id
```

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit http://localhost:8000/

## Usage

### Authentication

1. **Sign Up**: Visit `/accounts/signup/` to create an account
2. **Login**: Visit `/accounts/login/` to log in
3. **Logout**: Click logout in the navigation menu

### Finding Café Leads

#### Google Maps Search

1. Navigate to "Google Maps" in the menu
2. Enter a search query (e.g., "matcha café in Tokyo")
3. Review the results
4. Select cafés you want to save
5. Click "Save Selected Cafés"

#### Social Media Search (Apify)

1. Navigate to "Social Search" in the menu
2. Enter a search query (e.g., "matcha café Tokyo")
3. Select platform (TikTok or Instagram)
4. Click "Search"
5. Select accounts you want to save
6. Click "Save Selected Accounts"

### Managing Cafés

- **Browse All**: Visit "All Cafés" to see all collected leads
- **Filter**: Use the source and city filters
- **View Details**: Click "View" on any café
- **Edit**: Click "Edit" on the detail page to update information

### Admin Panel

Access the Django admin at `/admin/` to:
- Manage all cafés and search queries
- View detailed statistics
- Perform bulk actions

## Important Notes

### API Usage & Compliance

- **Google Maps**: Uses official Google Places API
- **Apify/Social Media**: 
  - TikTok/Instagram scraping via Apify must respect platform Terms of Service
  - This is for R&D and internal research purposes only
  - We DO NOT implement any automated messaging or DM functionality
  - We only discover and store public profile information

### Data Privacy

- This tool is for internal use only
- Store and handle data responsibly
- Comply with applicable data protection regulations

## Project Structure

```
rikyu_matcha_profile_collector/
├── sales_leads/           # Django project settings
│   ├── settings.py
│   └── urls.py
├── leads/                 # Main app
│   ├── models.py         # Cafe and SearchQuery models
│   ├── views.py          # All views
│   ├── forms.py          # Forms
│   ├── admin.py          # Admin configuration
│   ├── services/         # External API integrations
│   │   ├── google_maps.py
│   │   └── apify.py
│   └── urls/             # URL routing
│       ├── accounts.py   # Auth URLs
│       └── main.py       # Main URLs
├── templates/            # HTML templates
│   ├── base.html
│   ├── accounts/
│   └── leads/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Database Models

### Cafe

Stores café leads from various sources.

- `name`: Café name
- `city`: City location
- `address`: Full address
- `website`: Website URL
- `instagram_handle`: Instagram username
- `tiktok_handle`: TikTok username
- `source`: Source of the lead (google_maps, apify_tiktok, apify_instagram)
- `google_place_id`: Google Place ID
- `notes`: Additional notes
- `created_at`: Timestamp

### SearchQuery

Tracks search queries made to different platforms.

- `query_text`: Search query
- `platform`: Platform searched (google_maps, tiktok, instagram)
- `status`: Status (pending, running, done, failed)
- `created_by`: User who created the search
- `created_at`: Timestamp

## Troubleshooting

### Google Maps API Errors

- Ensure `GOOGLE_MAPS_API_KEY` is set in `.env`
- Check that the key has the Places API enabled
- Verify billing is enabled on your Google Cloud project

### Apify Errors

- Ensure `APIFY_TOKEN` is set in `.env`
- Verify the actor IDs are correct
- Check Apify dashboard for actor run status
- Some actors may take time to complete (5-30 seconds)

### Database Issues

If you need to reset the database:

```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## License

Internal use only - Friends Corp / Rikyu Matcha




