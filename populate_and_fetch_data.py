#!/usr/bin/env python
"""
Script to populate sample data and fetch data from API endpoints
"""
import os
import django
import requests
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'competitor_monitor.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from monitor.models import Competitor, CompetitorUpdate, Trend, Notification, MonitoringConfig, UpdateType

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def create_sample_data():
    """Create sample data for testing"""
    print_section("CREATING SAMPLE DATA")
    
    # Create or get user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_staff': True}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")
    
    # Create competitors
    competitors_data = [
        {
            'name': 'TechCorp Inc',
            'website': 'https://techcorp.example.com',
            'description': 'Leading technology solutions provider',
            'industry': 'Technology',
            'is_active': True
        },
        {
            'name': 'CloudServices Ltd',
            'website': 'https://cloudservices.example.com',
            'description': 'Cloud infrastructure and services',
            'industry': 'Cloud Computing',
            'is_active': True
        },
        {
            'name': 'DataAnalytics Pro',
            'website': 'https://dataanalytics.example.com',
            'description': 'Advanced data analytics platform',
            'industry': 'Data Analytics',
            'is_active': True
        }
    ]
    
    competitors = []
    for comp_data in competitors_data:
        competitor, created = Competitor.objects.get_or_create(
            name=comp_data['name'],
            defaults=comp_data
        )
        competitors.append(competitor)
        if created:
            print(f"Created competitor: {competitor.name}")
            # Create monitoring config
            MonitoringConfig.objects.create(
                competitor=competitor,
                check_interval_hours=24,
                is_enabled=True
            )
        else:
            print(f"Using existing competitor: {competitor.name}")
    
    # Create updates
    updates_data = [
        {
            'competitor': competitors[0],
            'title': 'New Pricing Model Launched',
            'content': 'TechCorp Inc has announced a new subscription-based pricing model with significant discounts for annual plans.',
            'url': 'https://techcorp.example.com/pricing',
            'update_type': UpdateType.PRICING,
            'impact_score': 85,
            'is_high_impact': True,
            'source': 'website',
            'detected_at': timezone.now() - timedelta(days=1)
        },
        {
            'competitor': competitors[0],
            'title': 'Product Release: Version 3.0',
            'content': 'TechCorp Inc has released version 3.0 of their flagship product with new AI-powered features.',
            'url': 'https://techcorp.example.com/release',
            'update_type': UpdateType.RELEASE,
            'impact_score': 90,
            'is_high_impact': True,
            'source': 'website',
            'detected_at': timezone.now() - timedelta(days=2)
        },
        {
            'competitor': competitors[1],
            'title': 'Summer Campaign: 50% Off',
            'content': 'CloudServices Ltd is running a summer promotion with 50% discount on all cloud storage plans.',
            'url': 'https://cloudservices.example.com/campaign',
            'update_type': UpdateType.CAMPAIGN,
            'impact_score': 70,
            'is_high_impact': True,
            'source': 'website',
            'detected_at': timezone.now() - timedelta(days=3)
        },
        {
            'competitor': competitors[1],
            'title': 'Partnership with Major Provider',
            'content': 'CloudServices Ltd announced a strategic partnership with a major cloud infrastructure provider.',
            'url': 'https://cloudservices.example.com/partnership',
            'update_type': UpdateType.PARTNERSHIP,
            'impact_score': 75,
            'is_high_impact': True,
            'source': 'website',
            'detected_at': timezone.now() - timedelta(days=4)
        },
        {
            'competitor': competitors[2],
            'title': 'New Feature: Real-time Analytics',
            'content': 'DataAnalytics Pro has added real-time analytics dashboard to their platform.',
            'url': 'https://dataanalytics.example.com/features',
            'update_type': UpdateType.FEATURE,
            'impact_score': 60,
            'is_high_impact': False,
            'source': 'website',
            'detected_at': timezone.now() - timedelta(days=5)
        },
        {
            'competitor': competitors[2],
            'title': 'Company News: Expansion Plans',
            'content': 'DataAnalytics Pro announced plans to expand operations to three new regions.',
            'url': 'https://dataanalytics.example.com/news',
            'update_type': UpdateType.NEWS,
            'impact_score': 50,
            'is_high_impact': False,
            'source': 'website',
            'detected_at': timezone.now() - timedelta(days=6)
        }
    ]
    
    updates = []
    for update_data in updates_data:
        update, created = CompetitorUpdate.objects.get_or_create(
            competitor=update_data['competitor'],
            title=update_data['title'],
            defaults=update_data
        )
        updates.append(update)
        if created:
            print(f"Created update: {update.title}")
    
    # Create notifications for high-impact updates
    for update in updates:
        if update.is_high_impact:
            notification, created = Notification.objects.get_or_create(
                user=user,
                update=update,
                defaults={
                    'message': f'High-impact update from {update.competitor.name}: {update.title}',
                    'is_read': False
                }
            )
            if created:
                print(f"Created notification for: {update.title}")
    
    # Create trends
    from monitor.services import TrendAnalyzer
    analyzer = TrendAnalyzer()
    trends = analyzer.detect_trends()
    if trends:
        print(f"Created {len(trends)} trends")
    
    print("\nSample data creation completed!")
    return competitors, updates

def fetch_api_data():
    """Fetch data from API endpoints"""
    print_section("FETCHING DATA FROM API")
    
    endpoints = {
        'Dashboard Stats': f'{BASE_URL}/dashboard/stats/',
        'Competitors': f'{BASE_URL}/competitors/',
        'Updates': f'{BASE_URL}/updates/',
        'High Impact Updates': f'{BASE_URL}/updates/?high_impact=true',
        'Trends': f'{BASE_URL}/trends/',
    }
    
    results = {}
    
    for name, url in endpoints.items():
        print(f"\n[{name}]")
        print(f"  URL: {url}")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results[name] = data
                
                # Display summary
                if isinstance(data, dict):
                    if 'count' in data:
                        print(f"  Count: {data['count']}")
                    if 'results' in data:
                        print(f"  Results: {len(data['results'])} items")
                        if data['results']:
                            print(f"  First item: {data['results'][0].get('name') or data['results'][0].get('title', 'N/A')}")
                    else:
                        # Dashboard stats
                        print(f"  Total Competitors: {data.get('total_competitors', 0)}")
                        print(f"  Total Updates: {data.get('total_updates', 0)}")
                        print(f"  High Impact: {data.get('high_impact_count', 0)}")
                print(f"  Status: SUCCESS")
            else:
                print(f"  Status: ERROR ({response.status_code})")
                results[name] = None
        except requests.exceptions.ConnectionError:
            print(f"  Status: ERROR - Server not running")
            print(f"  Please start the server with: python manage.py runserver")
            results[name] = None
        except Exception as e:
            print(f"  Status: ERROR - {str(e)}")
            results[name] = None
    
    return results

def display_data_summary(results):
    """Display a summary of fetched data"""
    print_section("DATA SUMMARY")
    
    if results.get('Dashboard Stats'):
        stats = results['Dashboard Stats']
        print(f"\nDashboard Statistics:")
        print(f"  Total Competitors: {stats.get('total_competitors', 0)}")
        print(f"  Total Updates: {stats.get('total_updates', 0)}")
        print(f"  High Impact Updates: {stats.get('high_impact_count', 0)}")
        print(f"  Updates This Week: {stats.get('recent_week_updates', 0)}")
        print(f"  Updates by Type: {stats.get('updates_by_type', {})}")
    
    if results.get('Competitors'):
        comps = results['Competitors']
        if comps.get('results'):
            print(f"\nCompetitors ({comps.get('count', 0)}):")
            for comp in comps['results'][:5]:  # Show first 5
                print(f"  - {comp.get('name')} ({comp.get('update_count', 0)} updates)")
    
    if results.get('Updates'):
        updates = results['Updates']
        if updates.get('results'):
            print(f"\nUpdates ({updates.get('count', 0)}):")
            for update in updates['results'][:5]:  # Show first 5
                print(f"  - {update.get('title')} ({update.get('update_type')}) - Impact: {update.get('impact_score', 0)}")
    
    if results.get('Trends'):
        trends = results['Trends']
        if trends.get('results'):
            print(f"\nTrends ({trends.get('count', 0)}):")
            for trend in trends['results']:
                print(f"  - {trend.get('name')} (Frequency: {trend.get('frequency', 0)})")

def save_data_to_file(results):
    """Save fetched data to JSON file"""
    filename = f"api_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Remove None values
    clean_results = {k: v for k, v in results.items() if v is not None}
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=2, default=str)
    
    print(f"\nData saved to: {filename}")

def main():
    print_section("COMPETITOR MONITOR - DATA POPULATION AND FETCHING")
    
    # Step 1: Create sample data
    create_sample_data()
    
    # Step 2: Fetch data from API
    results = fetch_api_data()
    
    # Step 3: Display summary
    display_data_summary(results)
    
    # Step 4: Save to file
    if any(results.values()):
        save_data_to_file(results)
    
    print_section("COMPLETED")
    print("\nNext steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Visit API in browser: http://127.0.0.1:8000/api/")
    print("3. Test endpoints: python test_api.py")

if __name__ == '__main__':
    main()

