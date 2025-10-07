from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class BotVisit(models.Model):
    """Track bot visits separately (for monitoring)"""
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    path = models.CharField(max_length=500)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    bot_type = models.CharField(max_length=100, blank=True)  # e.g., "googlebot", "curl"
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['bot_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.bot_type} - {self.path} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class PageView(models.Model):
    """Track every page view on the site"""
    url = models.CharField(max_length=500)
    path = models.CharField(max_length=500)
    page_title = models.CharField(max_length=200, blank=True)
    
    # Visitor info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField()
    
    # Geographic info
    country = models.CharField(max_length=100, blank=True, db_index=True)
    country_code = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    
    # Browser/Device info
    user_agent = models.TextField()
    browser = models.CharField(max_length=50, blank=True)
    device = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    
    # Referrer info
    referrer = models.CharField(max_length=500, blank=True)
    referrer_domain = models.CharField(max_length=200, blank=True)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    time_on_page = models.IntegerField(null=True, blank=True, help_text="Seconds spent on page")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'path']),
            models.Index(fields=['session_key', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['country', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.path} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Event(models.Model):
    """Track custom events (button clicks, form submissions, etc.)"""
    EVENT_TYPES = [
        ('click', 'Button Click'),
        ('form_submit', 'Form Submission'),
        ('payment', 'Payment Initiated'),
        ('signup', 'User Signup'),
        ('login', 'User Login'),
        ('download', 'File Download'),
        ('other', 'Other'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    event_name = models.CharField(max_length=200)
    event_data = models.JSONField(blank=True, null=True)
    
    # Visitor info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField()
    
    # Context
    page_url = models.CharField(max_length=500)
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['session_key', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type}: {self.event_name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
