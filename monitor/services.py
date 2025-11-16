"""
Service layer for monitoring and analyzing competitor data
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from .models import Competitor, CompetitorUpdate, UpdateType, Trend, Notification, MonitoringConfig
import logging

logger = logging.getLogger(__name__)


class CompetitorMonitor:
    """Main service for monitoring competitor websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_competitor_website(self, competitor):
        """Scrape updates from a competitor's website"""
        try:
            response = self.session.get(competitor.website, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract potential updates (this is a simplified version)
            # In production, you'd customize this per competitor
            updates = []
            
            # Look for common patterns: headings, article titles, etc.
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            articles = soup.find_all(['article', 'div'], class_=re.compile(r'post|article|news|update', re.I))
            
            for element in headings[:10] + articles[:10]:
                text = element.get_text(strip=True)
                if text and len(text) > 20:
                    updates.append({
                        'title': text[:200],
                        'content': text[:1000],
                        'url': competitor.website
                    })
            
            return updates[:5]  # Limit to 5 updates per check
            
        except Exception as e:
            logger.error(f"Error scraping {competitor.website}: {str(e)}")
            return []
    
    def classify_update(self, title, content):
        """Classify an update based on keywords and content"""
        text = (title + " " + content).lower()
        
        # Pricing keywords
        pricing_keywords = ['price', 'pricing', 'cost', '$', 'discount', 'sale', 'deal', 'offer', 'promotion']
        if any(keyword in text for keyword in pricing_keywords):
            return UpdateType.PRICING
        
        # Campaign keywords
        campaign_keywords = ['campaign', 'launch', 'advertising', 'marketing', 'promote', 'announce']
        if any(keyword in text for keyword in campaign_keywords):
            return UpdateType.CAMPAIGN
        
        # Release keywords
        release_keywords = ['release', 'launch', 'new product', 'introducing', 'unveil', 'debut']
        if any(keyword in text for keyword in release_keywords):
            return UpdateType.RELEASE
        
        # Partnership keywords
        partnership_keywords = ['partnership', 'partner', 'collaboration', 'alliance', 'joint']
        if any(keyword in text for keyword in partnership_keywords):
            return UpdateType.PARTNERSHIP
        
        # Feature keywords
        feature_keywords = ['feature', 'update', 'improvement', 'enhancement', 'new functionality']
        if any(keyword in text for keyword in feature_keywords):
            return UpdateType.FEATURE
        
        return UpdateType.OTHER
    
    def calculate_impact_score(self, title, content, update_type):
        """Calculate impact score (0-100) for an update"""
        score = 0
        text = (title + " " + content).lower()
        
        # High-impact keywords
        high_impact_keywords = ['launch', 'new', 'breakthrough', 'major', 'significant', 'revolutionary']
        score += sum(10 for keyword in high_impact_keywords if keyword in text)
        
        # Type-based scoring
        type_scores = {
            UpdateType.PRICING: 30,
            UpdateType.RELEASE: 40,
            UpdateType.CAMPAIGN: 25,
            UpdateType.PARTNERSHIP: 35,
            UpdateType.FEATURE: 20,
        }
        score += type_scores.get(update_type, 10)
        
        # Length-based (longer content might be more important)
        if len(content) > 500:
            score += 10
        
        return min(score, 100)
    
    def check_competitor(self, competitor):
        """Check a single competitor for updates"""
        config = MonitoringConfig.objects.filter(competitor=competitor).first()
        if not config or not config.is_enabled:
            return []
        
        # Check if it's time to check
        if config.last_checked:
            time_since_check = timezone.now() - config.last_checked
            if time_since_check < timedelta(hours=config.check_interval_hours):
                return []
        
        updates_data = self.scrape_competitor_website(competitor)
        new_updates = []
        
        for update_data in updates_data:
            # Check if update already exists
            existing = CompetitorUpdate.objects.filter(
                competitor=competitor,
                title__icontains=update_data['title'][:50]
            ).first()
            
            if not existing:
                update_type = self.classify_update(update_data['title'], update_data['content'])
                impact_score = self.calculate_impact_score(
                    update_data['title'], 
                    update_data['content'], 
                    update_type
                )
                
                update = CompetitorUpdate.objects.create(
                    competitor=competitor,
                    title=update_data['title'],
                    content=update_data['content'],
                    url=update_data.get('url', competitor.website),
                    update_type=update_type,
                    impact_score=impact_score,
                    is_high_impact=impact_score >= 60,
                    source='website'
                )
                new_updates.append(update)
        
        # Update last checked time
        if config:
            config.last_checked = timezone.now()
            config.save()
        
        return new_updates
    
    def check_all_competitors(self):
        """Check all active competitors"""
        competitors = Competitor.objects.filter(is_active=True)
        all_new_updates = []
        
        for competitor in competitors:
            try:
                updates = self.check_competitor(competitor)
                all_new_updates.extend(updates)
            except Exception as e:
                logger.error(f"Error checking competitor {competitor.name}: {str(e)}")
        
        # Create notifications for high-impact updates
        for update in all_new_updates:
            if update.is_high_impact:
                self.create_notifications(update)
        
        return all_new_updates
    
    def create_notifications(self, update):
        """Create notifications for all users about high-impact updates"""
        from django.contrib.auth.models import User
        users = User.objects.all()
        
        for user in users:
            Notification.objects.create(
                user=user,
                update=update,
                message=f"High-impact update from {update.competitor.name}: {update.title}"
            )


class TrendAnalyzer:
    """Analyzes trends and patterns in competitor updates"""
    
    def detect_trends(self, days=30):
        """Detect trends in the last N days"""
        cutoff_date = timezone.now() - timedelta(days=days)
        recent_updates = CompetitorUpdate.objects.filter(detected_at__gte=cutoff_date)
        
        trends = []
        
        # Detect trends by update type
        type_counts = recent_updates.values('update_type').annotate(
            count=Count('id')
        ).filter(count__gte=3)
        
        for item in type_counts:
            trend_name = f"Increase in {item['update_type']} updates"
            related_updates = recent_updates.filter(update_type=item['update_type'])
            
            trend, created = Trend.objects.get_or_create(
                name=trend_name,
                defaults={
                    'description': f"Detected {item['count']} {item['update_type']} updates in the last {days} days",
                    'trend_type': item['update_type'],
                    'frequency': item['count'],
                    'confidence_score': min(item['count'] / 10.0, 1.0)
                }
            )
            
            if not created:
                trend.frequency = item['count']
                trend.last_detected = timezone.now()
                trend.save()
            
            trend.related_updates.set(related_updates)
            trends.append(trend)
        
        # Detect competitor-specific trends
        competitor_counts = recent_updates.values('competitor__name').annotate(
            count=Count('id')
        ).filter(count__gte=5)
        
        for item in competitor_counts:
            trend_name = f"High activity from {item['competitor__name']}"
            related_updates = recent_updates.filter(competitor__name=item['competitor__name'])
            
            trend, created = Trend.objects.get_or_create(
                name=trend_name,
                defaults={
                    'description': f"{item['competitor__name']} has {item['count']} updates in the last {days} days",
                    'trend_type': 'competitor_activity',
                    'frequency': item['count'],
                    'confidence_score': min(item['count'] / 15.0, 1.0)
                }
            )
            
            if not created:
                trend.frequency = item['count']
                trend.last_detected = timezone.now()
                trend.save()
            
            trend.related_updates.set(related_updates)
            trends.append(trend)
        
        return trends


