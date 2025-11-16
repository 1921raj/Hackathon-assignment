from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Competitor, CompetitorUpdate, Trend, Notification, MonitoringConfig, UpdateType
from .services import CompetitorMonitor, TrendAnalyzer
from .forms import CompetitorForm, MonitoringConfigForm, SignUpForm


def dashboard(request):
    """Main dashboard view"""
    # Get recent updates
    recent_updates = CompetitorUpdate.objects.all()[:20]
    
    # Get statistics
    total_competitors = Competitor.objects.filter(is_active=True).count()
    total_updates = CompetitorUpdate.objects.count()
    high_impact_count = CompetitorUpdate.objects.filter(is_high_impact=True).count()
    
    # Updates by type
    updates_by_type = CompetitorUpdate.objects.values('update_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent trends
    recent_trends = Trend.objects.all()[:5]
    
    # Unread notifications
    unread_notifications = []
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user, 
            is_read=False
        )[:5]
    
    # Updates in last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    recent_week_updates = CompetitorUpdate.objects.filter(detected_at__gte=week_ago).count()
    
    context = {
        'recent_updates': recent_updates,
        'total_competitors': total_competitors,
        'total_updates': total_updates,
        'high_impact_count': high_impact_count,
        'updates_by_type': updates_by_type,
        'recent_trends': recent_trends,
        'unread_notifications': unread_notifications,
        'recent_week_updates': recent_week_updates,
        'update_types': UpdateType.choices,
    }
    
    return render(request, 'monitor/dashboard.html', context)


def competitors_list(request):
    """List all competitors"""
    competitors = Competitor.objects.all().annotate(
        update_count=Count('updates')
    )
    return render(request, 'monitor/competitors.html', {'competitors': competitors})


def competitor_detail(request, pk):
    """View details of a specific competitor"""
    competitor = get_object_or_404(Competitor, pk=pk)
    updates = competitor.updates.all()[:20]
    config = MonitoringConfig.objects.filter(competitor=competitor).first()
    
    context = {
        'competitor': competitor,
        'updates': updates,
        'config': config,
    }
    return render(request, 'monitor/competitor_detail.html', context)


@login_required
def add_competitor(request):
    """Add a new competitor"""
    if request.method == 'POST':
        form = CompetitorForm(request.POST)
        if form.is_valid():
            competitor = form.save()
            # Create default monitoring config
            MonitoringConfig.objects.create(
                competitor=competitor,
                check_interval_hours=24,
                is_enabled=True
            )
            messages.success(request, f'Competitor {competitor.name} added successfully!')
            return redirect('competitor_detail', pk=competitor.pk)
    else:
        form = CompetitorForm()
    
    return render(request, 'monitor/add_competitor.html', {'form': form})


def updates_list(request):
    """List all updates with filters"""
    updates = CompetitorUpdate.objects.all()
    
    # Filtering
    update_type = request.GET.get('type')
    if update_type:
        updates = updates.filter(update_type=update_type)
    
    high_impact = request.GET.get('high_impact')
    if high_impact == 'true':
        updates = updates.filter(is_high_impact=True)
    
    competitor_id = request.GET.get('competitor')
    if competitor_id:
        updates = updates.filter(competitor_id=competitor_id)
    
    updates = updates[:50]  # Limit results
    
    competitors = Competitor.objects.all()
    
    context = {
        'updates': updates,
        'competitors': competitors,
        'update_types': UpdateType.choices,
        'current_filters': {
            'type': update_type,
            'high_impact': high_impact,
            'competitor': competitor_id,
        }
    }
    
    return render(request, 'monitor/updates.html', context)


def update_detail(request, pk):
    """View details of a specific update"""
    update = get_object_or_404(CompetitorUpdate, pk=pk)
    related_trends = update.trends.all()
    
    context = {
        'update': update,
        'related_trends': related_trends,
    }
    return render(request, 'monitor/update_detail.html', context)


def trends_list(request):
    """List all detected trends"""
    trends = Trend.objects.all()
    
    # Run trend analysis if requested (only for authenticated users)
    if request.GET.get('analyze') == 'true' and request.user.is_authenticated:
        analyzer = TrendAnalyzer()
        analyzer.detect_trends()
        messages.success(request, 'Trend analysis completed!')
        return redirect('trends')
    
    context = {
        'trends': trends,
    }
    return render(request, 'monitor/trends.html', context)


@login_required
def notifications_list(request):
    """List user's notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark as read if requested
    if request.GET.get('mark_read') == 'all':
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read!')
        return redirect('notifications')
    
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'monitor/notifications.html', context)


@login_required
def mark_notification_read(request, pk):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, 'Notification marked as read!')
    return redirect('notifications')


def run_monitoring(request):
    """Manually trigger competitor monitoring"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to run monitoring.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        monitor = CompetitorMonitor()
        new_updates = monitor.check_all_competitors()
        messages.success(request, f'Monitoring completed! Found {len(new_updates)} new updates.')
        return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def monitoring_config(request, pk):
    """Configure monitoring for a competitor"""
    competitor = get_object_or_404(Competitor, pk=pk)
    config = MonitoringConfig.objects.filter(competitor=competitor).first()
    
    if request.method == 'POST':
        form = MonitoringConfigForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.competitor = competitor
            config.save()
            messages.success(request, 'Monitoring configuration updated!')
            return redirect('competitor_detail', pk=competitor.pk)
    else:
        form = MonitoringConfigForm(instance=config)
    
    context = {
        'form': form,
        'competitor': competitor,
    }
    return render(request, 'monitor/monitoring_config.html', context)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next', 'dashboard')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    context = {
        'next': request.GET.get('next', ''),
        'show_signup': False
    }
    return render(request, 'monitor/login.html', context)


def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
        'show_signup': True,
        'next': request.GET.get('next', '')
    }
    return render(request, 'monitor/login.html', context)


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('dashboard')


