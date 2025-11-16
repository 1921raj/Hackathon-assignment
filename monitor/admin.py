from django.contrib import admin
from .models import Competitor, CompetitorUpdate, Trend, Notification, MonitoringConfig


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'industry', 'is_active', 'created_at']
    list_filter = ['is_active', 'industry', 'created_at']
    search_fields = ['name', 'website', 'description']


@admin.register(CompetitorUpdate)
class CompetitorUpdateAdmin(admin.ModelAdmin):
    list_display = ['title', 'competitor', 'update_type', 'impact_score', 'is_high_impact', 'detected_at']
    list_filter = ['update_type', 'is_high_impact', 'detected_at', 'source']
    search_fields = ['title', 'content', 'competitor__name']
    date_hierarchy = 'detected_at'


@admin.register(Trend)
class TrendAdmin(admin.ModelAdmin):
    list_display = ['name', 'trend_type', 'frequency', 'confidence_score', 'last_detected']
    list_filter = ['trend_type', 'last_detected']
    search_fields = ['name', 'description']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'update', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']


@admin.register(MonitoringConfig)
class MonitoringConfigAdmin(admin.ModelAdmin):
    list_display = ['competitor', 'check_interval_hours', 'is_enabled', 'last_checked']
    list_filter = ['is_enabled']


