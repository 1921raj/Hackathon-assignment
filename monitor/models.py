from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Competitor(models.Model):
    """Represents a competitor company being monitored"""
    name = models.CharField(max_length=200)
    website = models.URLField()
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UpdateType(models.TextChoices):
    PRICING = 'pricing', 'Pricing Change'
    CAMPAIGN = 'campaign', 'Marketing Campaign'
    RELEASE = 'release', 'Product Release'
    PARTNERSHIP = 'partnership', 'Partnership'
    NEWS = 'news', 'News/Announcement'
    FEATURE = 'feature', 'Feature Update'
    OTHER = 'other', 'Other'


class CompetitorUpdate(models.Model):
    """Stores individual updates from competitors"""
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=500)
    content = models.TextField()
    url = models.URLField(blank=True)
    update_type = models.CharField(max_length=20, choices=UpdateType.choices, default=UpdateType.OTHER)
    detected_at = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(null=True, blank=True)
    impact_score = models.IntegerField(default=0, help_text="0-100 scale for impact assessment")
    is_high_impact = models.BooleanField(default=False)
    source = models.CharField(max_length=100, default='website', help_text="Source: website, social, etc.")
    
    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['-detected_at']),
            models.Index(fields=['update_type']),
            models.Index(fields=['is_high_impact']),
        ]
    
    def __str__(self):
        return f"{self.competitor.name}: {self.title[:50]}"


class Trend(models.Model):
    """Detected trends and patterns across competitor updates"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    trend_type = models.CharField(max_length=50)
    frequency = models.IntegerField(help_text="Number of occurrences")
    first_detected = models.DateTimeField(auto_now_add=True)
    last_detected = models.DateTimeField(auto_now=True)
    related_updates = models.ManyToManyField(CompetitorUpdate, related_name='trends')
    confidence_score = models.FloatField(default=0.0, help_text="0-1 scale")
    
    class Meta:
        ordering = ['-last_detected']
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """Notifications for high-impact competitor actions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    update = models.ForeignKey(CompetitorUpdate, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.update.title[:50]}"


class MonitoringConfig(models.Model):
    """Configuration for monitoring each competitor"""
    competitor = models.OneToOneField(Competitor, on_delete=models.CASCADE, related_name='monitoring_config')
    check_interval_hours = models.IntegerField(default=24, help_text="Hours between checks")
    last_checked = models.DateTimeField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords to monitor")
    
    def __str__(self):
        return f"Monitoring config for {self.competitor.name}"



