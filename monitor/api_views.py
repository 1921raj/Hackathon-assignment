from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Competitor, CompetitorUpdate, Trend, Notification, MonitoringConfig, UpdateType
from .serializers import (
    CompetitorSerializer, CompetitorUpdateSerializer, TrendSerializer,
    NotificationSerializer, MonitoringConfigSerializer, DashboardStatsSerializer
)
from .services import CompetitorMonitor, TrendAnalyzer


class CompetitorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing competitors.
    """
    queryset = Competitor.objects.all().annotate(update_count=Count('updates'))
    serializer_class = CompetitorSerializer
    
    def get_queryset(self):
        queryset = Competitor.objects.all().annotate(update_count=Count('updates'))
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset


class CompetitorUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing competitor updates.
    """
    queryset = CompetitorUpdate.objects.all()
    serializer_class = CompetitorUpdateSerializer
    
    def get_queryset(self):
        queryset = CompetitorUpdate.objects.all()
        
        # Filter by competitor
        competitor_id = self.request.query_params.get('competitor', None)
        if competitor_id:
            queryset = queryset.filter(competitor_id=competitor_id)
        
        # Filter by update type
        update_type = self.request.query_params.get('type', None)
        if update_type:
            queryset = queryset.filter(update_type=update_type)
        
        # Filter by high impact
        high_impact = self.request.query_params.get('high_impact', None)
        if high_impact is not None:
            queryset = queryset.filter(is_high_impact=high_impact.lower() == 'true')
        
        # Filter by date range
        days = self.request.query_params.get('days', None)
        if days:
            try:
                days = int(days)
                cutoff_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(detected_at__gte=cutoff_date)
            except ValueError:
                pass
        
        return queryset.order_by('-detected_at')


class TrendViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing trends.
    """
    queryset = Trend.objects.all()
    serializer_class = TrendSerializer
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Trigger trend analysis"""
        analyzer = TrendAnalyzer()
        trends = analyzer.detect_trends()
        serializer = self.get_serializer(trends, many=True)
        return Response({
            'message': f'Trend analysis completed. Found {len(trends)} trends.',
            'trends': serializer.data
        })


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing notifications.
    """
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        # Only return notifications for the authenticated user
        if self.request.user.is_authenticated:
            return Notification.objects.filter(user=self.request.user)
        return Notification.objects.none()
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        notification = self.get_object()
        if notification.user != request.user:
            return Response({'error': 'Permission denied'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})


@api_view(['GET'])
def dashboard_stats(request):
    """
    API endpoint for dashboard statistics.
    """
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
    
    data = {
        'total_competitors': total_competitors,
        'total_updates': total_updates,
        'high_impact_count': high_impact_count,
        'recent_week_updates': recent_week_updates,
        'updates_by_type': updates_by_type,
    }
    
    serializer = DashboardStatsSerializer(data)
    if serializer.is_valid():
        return Response(serializer.validated_data)
    return Response(data)  # Return data directly if serializer fails


@api_view(['POST'])
def run_monitoring(request):
    """
    API endpoint to trigger competitor monitoring.
    Note: REST Framework automatically handles CSRF for API views.
    """
    monitor = CompetitorMonitor()
    new_updates = monitor.check_all_competitors()
    
    return Response({
        'message': 'Monitoring completed',
        'new_updates_count': len(new_updates),
        'updates': CompetitorUpdateSerializer(new_updates, many=True).data
    })

