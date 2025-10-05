from django.contrib.sitemaps import Sitemap
from blog.models import Post


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            '/',
            '/pricing/',
            '/pricing/assignments/',
            '/portfolio/',
            '/blog/',
            '/login/',
            '/signup/',
        ]

    def location(self, item):
        return item


class BlogPostSitemap(Sitemap):
    """Sitemap for blog posts"""
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        # Only include published posts
        return Post.objects.filter(status='published').order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f'/blog/{obj.slug}/'
