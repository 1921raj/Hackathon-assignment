from rest_framework import serializers
from .models import Competitor, CompetitorUpdate, Trend, Notification, MonitoringConfig


class CompetitorSerializer(serializers.ModelSerializer):
    update_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Competitor
        fields = ['id', 'name', 'website', 'description', 'industry', 'is_active', 
                  'created_at', 'update_count']


class CompetitorUpdateSerializer(serializers.ModelSerializer):
    competitor_name = serializers.CharField(source='competitor.name', read_only=True)
    competitor_id = serializers.IntegerField(source='competitor.id', read_only=True)
    
    class Meta:
        model = CompetitorUpdate
        fields = ['id', 'competitor_id', 'competitor_name', 'title', 'content', 'url',
                  'update_type', 'detected_at', 'published_date', 'impact_score',
                  'is_high_impact', 'source']


class TrendSerializer(serializers.ModelSerializer):
    related_updates_count = serializers.IntegerField(source='related_updates.count', read_only=True)
    
    class Meta:
        model = Trend
        fields = ['id', 'name', 'description', 'trend_type', 'frequency',
                  'first_detected', 'last_detected', 'confidence_score', 'related_updates_count']


class NotificationSerializer(serializers.ModelSerializer):
    update_title = serializers.CharField(source='update.title', read_only=True)
    competitor_name = serializers.CharField(source='update.competitor.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'update_title', 'competitor_name', 'message', 'is_read', 'created_at']


class MonitoringConfigSerializer(serializers.ModelSerializer):
    competitor_name = serializers.CharField(source='competitor.name', read_only=True)
    
    class Meta:
        model = MonitoringConfig
        fields = ['id', 'competitor_name', 'check_interval_hours', 'is_enabled',
                  'last_checked', 'keywords']


class DashboardStatsSerializer(serializers.Serializer):
    total_competitors = serializers.IntegerField()
    total_updates = serializers.IntegerField()
    high_impact_count = serializers.IntegerField()
    recent_week_updates = serializers.IntegerField()
    updates_by_type = serializers.DictField()

