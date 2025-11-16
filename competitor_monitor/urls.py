"""
URL configuration for competitor_monitor project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from monitor import api_views

# API Router
router = DefaultRouter()
router.register(r'api/competitors', api_views.CompetitorViewSet, basename='competitor')
router.register(r'api/updates', api_views.CompetitorUpdateViewSet, basename='update')
router.register(r'api/trends', api_views.TrendViewSet, basename='trend')
router.register(r'api/notifications', api_views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('monitor.urls')),
    path('api/dashboard/stats/', api_views.dashboard_stats, name='api-dashboard-stats'),
    path('api/monitor/run/', api_views.run_monitoring, name='api-run-monitoring'),
    path('api/', include(router.urls)),
]



