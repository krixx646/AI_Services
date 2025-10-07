import re
import requests
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from .models import PageView, BotVisit


class AnalyticsMiddleware(MiddlewareMixin):
    """Automatically track page views"""
    
    # Paths to exclude from tracking
    EXCLUDE_PATHS = [
        r'^/admin/',
        r'^/static/',
        r'^/media/',
        r'^/api/',
        r'^/cms/',
        r'^/favicon\.ico$',
        r'^/robots\.txt$',
    ]
    
    def is_bot(self, user_agent):
        """Detect if the user agent is a bot - returns (is_bot, bot_type)"""
        if not user_agent:
            return True, 'empty-user-agent'
        
        user_agent_lower = user_agent.lower()
        
        # Common bot indicators
        bot_patterns = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
            'python-requests', 'java', 'http', 'headless', 'phantom',
            'selenium', 'playwright', 'puppeteer', 'slurp', 'bingpreview',
            'googlebot', 'bingbot', 'yandexbot', 'baiduspider', 'facebookexternalhit',
            'twitterbot', 'linkedinbot', 'whatsapp', 'telegrambot', 'slackbot',
            'discordbot', 'petalbot', 'ahrefsbot', 'semrushbot', 'mj12bot',
            'dotbot', 'rogerbot', 'exabot', 'screaming frog', 'archive.org',
        ]
        
        for pattern in bot_patterns:
            if pattern in user_agent_lower:
                return True, pattern
        
        return False, None
    
    def process_response(self, request, response):
        # Only track successful GET requests
        if request.method != 'GET' or response.status_code != 200:
            return response
        
        # Check if path should be excluded
        path = request.path
        for pattern in self.EXCLUDE_PATHS:
            if re.match(pattern, path):
                return response
        
        # Exclude admin/staff users from analytics
        if request.user.is_authenticated and request.user.is_staff:
            return response
        
        # Check for analytics exclusion cookie
        if request.COOKIES.get('exclude_analytics') == 'true':
            return response
        
        # Check for exclusion URL parameter
        if request.GET.get('exclude_analytics') == 'true':
            return response
        
        # Check for bots and log them separately
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        is_bot, bot_type = self.is_bot(user_agent)
        
        if is_bot:
            # Log bot visit for monitoring (don't count in regular analytics)
            try:
                ip_address = self.get_client_ip(request)
                BotVisit.objects.create(
                    path=request.path,
                    user_agent=user_agent[:500],  # Truncate if too long
                    ip_address=ip_address,
                    bot_type=bot_type or 'unknown',
                )
            except Exception:
                pass  # Don't break if bot logging fails
            
            return response  # Don't track in regular analytics
        
        try:
            # Get or create session key
            if not request.session.session_key:
                request.session.create()
            
            # Extract browser/device info from user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            browser, device, os_name = self.parse_user_agent(user_agent)
            
            # Get referrer info
            referrer = request.META.get('HTTP_REFERER', '')
            referrer_domain = self.extract_domain(referrer) if referrer else ''
            
            # Get IP address
            ip_address = self.get_client_ip(request)
            
            # Get geographic info
            geo_data = self.get_geo_data(ip_address)
            
            # Create page view record
            PageView.objects.create(
                url=request.build_absolute_uri(),
                path=path,
                page_title=self.extract_page_title(response),
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key,
                ip_address=ip_address,
                country=geo_data.get('country', ''),
                country_code=geo_data.get('country_code', ''),
                city=geo_data.get('city', ''),
                region=geo_data.get('region', ''),
                user_agent=user_agent,
                browser=browser,
                device=device,
                os=os_name,
                referrer=referrer,
                referrer_domain=referrer_domain,
            )
        except Exception as e:
            # Silently fail - don't break the site if analytics fails
            pass
        
        return response
    
    def get_client_ip(self, request):
        """Extract client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
    
    def parse_user_agent(self, user_agent):
        """Simple user agent parsing"""
        ua_lower = user_agent.lower()
        
        # Browser detection
        if 'chrome' in ua_lower and 'edg' not in ua_lower:
            browser = 'Chrome'
        elif 'firefox' in ua_lower:
            browser = 'Firefox'
        elif 'safari' in ua_lower and 'chrome' not in ua_lower:
            browser = 'Safari'
        elif 'edg' in ua_lower:
            browser = 'Edge'
        elif 'opera' in ua_lower or 'opr' in ua_lower:
            browser = 'Opera'
        else:
            browser = 'Other'
        
        # Device detection
        if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
            device = 'Mobile'
        elif 'tablet' in ua_lower or 'ipad' in ua_lower:
            device = 'Tablet'
        else:
            device = 'Desktop'
        
        # OS detection
        if 'windows' in ua_lower:
            os_name = 'Windows'
        elif 'mac' in ua_lower:
            os_name = 'macOS'
        elif 'linux' in ua_lower:
            os_name = 'Linux'
        elif 'android' in ua_lower:
            os_name = 'Android'
        elif 'ios' in ua_lower or 'iphone' in ua_lower or 'ipad' in ua_lower:
            os_name = 'iOS'
        else:
            os_name = 'Other'
        
        return browser, device, os_name
    
    def extract_domain(self, url):
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ''
    
    def get_geo_data(self, ip_address):
        """Get geographic data from IP address using free API"""
        # Skip for local IPs
        if ip_address in ['127.0.0.1', '0.0.0.0', 'localhost'] or ip_address.startswith('192.168.'):
            return {
                'country': 'Local',
                'country_code': 'XX',
                'city': 'Local',
                'region': 'Local'
            }
        
        # Check cache first (cache for 24 hours)
        cache_key = f'geo_{ip_address}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Use free ip-api.com service (no API key required, 45 requests/minute)
            response = requests.get(
                f'http://ip-api.com/json/{ip_address}',
                timeout=2
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    geo_data = {
                        'country': data.get('country', ''),
                        'country_code': data.get('countryCode', ''),
                        'city': data.get('city', ''),
                        'region': data.get('regionName', '')
                    }
                    # Cache for 24 hours
                    cache.set(cache_key, geo_data, 86400)
                    return geo_data
        except Exception as e:
            # Silently fail and return empty data
            pass
        
        return {
            'country': '',
            'country_code': '',
            'city': '',
            'region': ''
        }
    
    def extract_page_title(self, response):
        """Try to extract page title from HTML"""
        try:
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8', errors='ignore')
                match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()[:200]
        except:
            pass
        return ''
