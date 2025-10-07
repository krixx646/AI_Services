from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta
from .models import PageView, Event, BotVisit


def is_staff(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def analytics_dashboard(request):
    """Main analytics dashboard - staff only"""
    
    # Time ranges
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Total stats
    total_views = PageView.objects.count()
    total_visitors = PageView.objects.values('session_key').distinct().count()
    total_events = Event.objects.count()
    
    # Today's stats
    today_views = PageView.objects.filter(timestamp__date=today).count()
    today_visitors = PageView.objects.filter(timestamp__date=today).values('session_key').distinct().count()
    
    # Yesterday's stats
    yesterday_views = PageView.objects.filter(timestamp__date=yesterday).count()
    yesterday_visitors = PageView.objects.filter(timestamp__date=yesterday).values('session_key').distinct().count()
    
    # Week stats
    week_views = PageView.objects.filter(timestamp__gte=week_ago).count()
    week_visitors = PageView.objects.filter(timestamp__gte=week_ago).values('session_key').distinct().count()
    
    # Month stats
    month_views = PageView.objects.filter(timestamp__gte=month_ago).count()
    month_visitors = PageView.objects.filter(timestamp__gte=month_ago).values('session_key').distinct().count()
    
    # Top pages (last 30 days)
    top_pages = PageView.objects.filter(
        timestamp__gte=month_ago
    ).values('path', 'page_title').annotate(
        views=Count('id')
    ).order_by('-views')[:10]
    
    # Traffic by day (last 30 days)
    daily_traffic = PageView.objects.filter(
        timestamp__gte=month_ago
    ).annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        views=Count('id'),
        visitors=Count('session_key', distinct=True)
    ).order_by('date')
    
    # Traffic by hour (last 24 hours)
    hourly_traffic = PageView.objects.filter(
        timestamp__gte=now - timedelta(hours=24)
    ).annotate(
        hour=TruncHour('timestamp')
    ).values('hour').annotate(
        views=Count('id')
    ).order_by('hour')
    
    # Browser stats
    browser_stats = PageView.objects.filter(
        timestamp__gte=month_ago
    ).values('browser').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Device stats
    device_stats = PageView.objects.filter(
        timestamp__gte=month_ago
    ).values('device').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # OS stats
    os_stats = PageView.objects.filter(
        timestamp__gte=month_ago
    ).values('os').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Top referrers
    top_referrers = PageView.objects.filter(
        timestamp__gte=month_ago,
        referrer_domain__isnull=False
    ).exclude(
        referrer_domain=''
    ).exclude(
        referrer_domain__contains='krixx.pythonanywhere.com'
    ).values('referrer_domain').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Geographic stats - Top countries
    top_countries = PageView.objects.filter(
        timestamp__gte=month_ago,
        country__isnull=False
    ).exclude(
        country=''
    ).exclude(
        country='Local'
    ).values('country', 'country_code').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top cities
    top_cities = PageView.objects.filter(
        timestamp__gte=month_ago,
        city__isnull=False
    ).exclude(
        city=''
    ).exclude(
        city='Local'
    ).values('city', 'country').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Recent events
    recent_events = Event.objects.select_related('user').order_by('-timestamp')[:20]
    
    # Bot statistics
    total_bots = BotVisit.objects.count()
    today_bots = BotVisit.objects.filter(timestamp__date=today).count()
    week_bots = BotVisit.objects.filter(timestamp__gte=week_ago).count()
    month_bots = BotVisit.objects.filter(timestamp__gte=month_ago).count()
    
    # Top bot types (last 30 days)
    top_bots = BotVisit.objects.filter(
        timestamp__gte=month_ago
    ).values('bot_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Recent bot visits
    recent_bots = BotVisit.objects.order_by('-timestamp')[:20]
    
    # Calculate growth rates
    views_growth = calculate_growth(today_views, yesterday_views)
    visitors_growth = calculate_growth(today_visitors, yesterday_visitors)
    
    context = {
        # Totals
        'total_views': total_views,
        'total_visitors': total_visitors,
        'total_events': total_events,
        
        # Today
        'today_views': today_views,
        'today_visitors': today_visitors,
        'views_growth': views_growth,
        'visitors_growth': visitors_growth,
        
        # Week
        'week_views': week_views,
        'week_visitors': week_visitors,
        
        # Month
        'month_views': month_views,
        'month_visitors': month_visitors,
        
        # Charts data
        'top_pages': top_pages,
        'daily_traffic': list(daily_traffic),
        'hourly_traffic': list(hourly_traffic),
        'browser_stats': list(browser_stats),
        'device_stats': list(device_stats),
        'os_stats': list(os_stats),
        'top_referrers': list(top_referrers),
        'top_countries': list(top_countries),
        'top_cities': list(top_cities),
        'recent_events': recent_events,
        
        # Bot stats
        'total_bots': total_bots,
        'today_bots': today_bots,
        'week_bots': week_bots,
        'month_bots': month_bots,
        'top_bots': list(top_bots),
        'recent_bots': recent_bots,
    }
    
    return render(request, 'analytics/dashboard.html', context)


def calculate_growth(current, previous):
    """Calculate percentage growth"""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 1)


def exclude_from_analytics(request):
    """Page to exclude/include user from analytics tracking"""
    # Check if user is currently excluded
    excluded = False
    
    # Check cookie
    if request.COOKIES.get('exclude_analytics') == 'true':
        excluded = True
    
    # Staff users are auto-excluded
    if request.user.is_authenticated and request.user.is_staff:
        excluded = True
    
    return render(request, 'analytics/exclude.html', {'excluded': excluded})
