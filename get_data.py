#!/usr/bin/env python
"""
Script to get and display data for competitors, updates, trends, and notifications
"""
import os
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'competitor_monitor.settings')
django.setup()

from monitor.models import Competitor, CompetitorUpdate, Trend, Notification, UpdateType
from django.db.models import Count

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def get_competitors_data():
    """Get all competitors data"""
    print_section("COMPETITORS")
    
    competitors = Competitor.objects.all().annotate(update_count=Count('updates'))
    
    if not competitors.exists():
        print("No competitors found.")
        return []
    
    data = []
    for comp in competitors:
        comp_data = {
            'id': comp.id,
            'name': comp.name,
            'website': comp.website,
            'description': comp.description,
            'industry': comp.industry,
            'is_active': comp.is_active,
            'created_at': comp.created_at.isoformat(),
            'update_count': comp.update_count
        }
        data.append(comp_data)
        print(f"\n[{comp.id}] {comp.name}")
        print(f"  Website: {comp.website}")
        print(f"  Industry: {comp.industry}")
        print(f"  Status: {'Active' if comp.is_active else 'Inactive'}")
        print(f"  Updates: {comp.update_count}")
        print(f"  Created: {comp.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\nTotal Competitors: {len(data)}")
    return data

def get_updates_data():
    """Get all updates data"""
    print_section("COMPETITOR UPDATES")
    
    updates = CompetitorUpdate.objects.all().order_by('-detected_at')
    
    if not updates.exists():
        print("No updates found.")
        return []
    
    data = []
    for update in updates:
        update_data = {
            'id': update.id,
            'competitor_id': update.competitor.id,
            'competitor_name': update.competitor.name,
            'title': update.title,
            'content': update.content[:200] + '...' if len(update.content) > 200 else update.content,
            'url': update.url,
            'update_type': update.update_type,
            'update_type_display': update.get_update_type_display(),
            'detected_at': update.detected_at.isoformat(),
            'published_date': update.published_date.isoformat() if update.published_date else None,
            'impact_score': update.impact_score,
            'is_high_impact': update.is_high_impact,
            'source': update.source
        }
        data.append(update_data)
        print(f"\n[{update.id}] {update.title}")
        print(f"  Competitor: {update.competitor.name}")
        print(f"  Type: {update.get_update_type_display()}")
        print(f"  Impact Score: {update.impact_score} {'(HIGH IMPACT)' if update.is_high_impact else ''}")
        print(f"  Detected: {update.detected_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Content: {update.content[:100]}...")
    
    # Statistics
    print(f"\n--- Statistics ---")
    print(f"Total Updates: {len(data)}")
    print(f"High Impact: {sum(1 for u in data if u['is_high_impact'])}")
    
    # By type
    type_counts = {}
    for update in updates:
        type_counts[update.get_update_type_display()] = type_counts.get(update.get_update_type_display(), 0) + 1
    
    print(f"\nUpdates by Type:")
    for update_type, count in type_counts.items():
        print(f"  {update_type}: {count}")
    
    return data

def get_trends_data():
    """Get all trends data"""
    print_section("TRENDS")
    
    trends = Trend.objects.all().order_by('-last_detected')
    
    if not trends.exists():
        print("No trends found.")
        print("\nTo create trends, run trend analysis from the web interface or API.")
        return []
    
    data = []
    for trend in trends:
        trend_data = {
            'id': trend.id,
            'name': trend.name,
            'description': trend.description,
            'trend_type': trend.trend_type,
            'frequency': trend.frequency,
            'first_detected': trend.first_detected.isoformat(),
            'last_detected': trend.last_detected.isoformat(),
            'confidence_score': float(trend.confidence_score),
            'related_updates_count': trend.related_updates.count()
        }
        data.append(trend_data)
        print(f"\n[{trend.id}] {trend.name}")
        print(f"  Type: {trend.trend_type}")
        print(f"  Frequency: {trend.frequency}")
        print(f"  Confidence: {trend.confidence_score:.2%}")
        print(f"  Related Updates: {trend.related_updates.count()}")
        print(f"  First Detected: {trend.first_detected.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Last Detected: {trend.last_detected.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Description: {trend.description}")
    
    print(f"\nTotal Trends: {len(data)}")
    return data

def get_notifications_data():
    """Get all notifications data"""
    print_section("NOTIFICATIONS")
    
    notifications = Notification.objects.all().order_by('-created_at')
    
    if not notifications.exists():
        print("No notifications found.")
        return []
    
    data = []
    for notif in notifications:
        notif_data = {
            'id': notif.id,
            'user': notif.user.username,
            'update_id': notif.update.id,
            'update_title': notif.update.title,
            'competitor_name': notif.update.competitor.name,
            'message': notif.message,
            'is_read': notif.is_read,
            'created_at': notif.created_at.isoformat()
        }
        data.append(notif_data)
        print(f"\n[{notif.id}] {notif.update.competitor.name}")
        print(f"  User: {notif.user.username}")
        print(f"  Update: {notif.update.title}")
        print(f"  Status: {'Read' if notif.is_read else 'Unread'}")
        print(f"  Created: {notif.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Message: {notif.message}")
    
    # Statistics
    print(f"\n--- Statistics ---")
    print(f"Total Notifications: {len(data)}")
    print(f"Unread: {sum(1 for n in data if not n['is_read'])}")
    print(f"Read: {sum(1 for n in data if n['is_read'])}")
    
    return data

def get_dashboard_stats():
    """Get dashboard statistics"""
    print_section("DASHBOARD STATISTICS")
    
    from django.utils import timezone
    from datetime import timedelta
    
    total_competitors = Competitor.objects.filter(is_active=True).count()
    total_updates = CompetitorUpdate.objects.count()
    high_impact_count = CompetitorUpdate.objects.filter(is_high_impact=True).count()
    
    week_ago = timezone.now() - timedelta(days=7)
    recent_week_updates = CompetitorUpdate.objects.filter(detected_at__gte=week_ago).count()
    
    updates_by_type = dict(
        CompetitorUpdate.objects.values('update_type')
        .annotate(count=Count('id'))
        .values_list('update_type', 'count')
    )
    
    stats = {
        'total_competitors': total_competitors,
        'total_updates': total_updates,
        'high_impact_count': high_impact_count,
        'recent_week_updates': recent_week_updates,
        'updates_by_type': updates_by_type
    }
    
    print(f"Total Active Competitors: {stats['total_competitors']}")
    print(f"Total Updates: {stats['total_updates']}")
    print(f"High Impact Updates: {stats['high_impact_count']}")
    print(f"Updates This Week: {stats['recent_week_updates']}")
    print(f"\nUpdates by Type:")
    for update_type, count in stats['updates_by_type'].items():
        print(f"  {update_type}: {count}")
    
    return stats

def save_to_json(all_data):
    """Save all data to JSON file"""
    filename = f"data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nAll data saved to: {filename}")
    return filename

def main():
    print_section("COMPETITOR MONITOR - DATA RETRIEVAL")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get all data
    dashboard_stats = get_dashboard_stats()
    competitors = get_competitors_data()
    updates = get_updates_data()
    trends = get_trends_data()
    notifications = get_notifications_data()
    
    # Combine all data
    all_data = {
        'exported_at': datetime.now().isoformat(),
        'dashboard_stats': dashboard_stats,
        'competitors': competitors,
        'updates': updates,
        'trends': trends,
        'notifications': notifications
    }
    
    # Save to file
    filename = save_to_json(all_data)
    
    print_section("SUMMARY")
    print(f"Competitors: {len(competitors)}")
    print(f"Updates: {len(updates)}")
    print(f"Trends: {len(trends)}")
    print(f"Notifications: {len(notifications)}")
    print(f"\nData exported to: {filename}")
    
    print("\nTo view this data via API:")
    print("1. Start server: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/api/")

if __name__ == '__main__':
    main()

