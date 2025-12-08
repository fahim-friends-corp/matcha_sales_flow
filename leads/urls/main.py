"""
Main URLs for the leads app (dashboard, searches, café management).
"""
from django.urls import path
from leads import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Google Maps Search
    path('google-search/', views.google_search_view, name='google_search'),
    
    # Apify Search (TikTok/Instagram)
    path('apify-search/', views.apify_search_view, name='apify_search'),
    
    # Café List and Detail
    path('cafes/', views.cafe_list_view, name='cafe_list'),
    path('cafes/<int:pk>/', views.CafeDetailView.as_view(), name='cafe_detail'),
    path('cafes/<int:pk>/edit/', views.CafeUpdateView.as_view(), name='cafe_update'),
]




