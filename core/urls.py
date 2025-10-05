"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import SearchView, PricingPageView
from accounts.views import LoginPageView, SignupPageView, ProfilePageView, LogoutView, DashboardView
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.http import JsonResponse
from blog import views as blog_views



urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API namespaces
    path('api/accounts/', include('accounts.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/bots/', include('bots.urls')),
    path('api/demo/', include('demo.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/processing/', include('processing.urls')),
    path('portfolio/', include('portfolio.urls')),

    # API schema and docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/search/', SearchView.as_view(), name='global-search'),
    path('api/health/', lambda r: JsonResponse({'status': 'ok'}), name='health'),

    # Site routes (templates)
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('assignments/', TemplateView.as_view(template_name='index_assignments.html'), name='assignments_home'),
    path('blog/', blog_views.SiteBlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', blog_views.SiteBlogDetailView.as_view(), name='blog_detail'),
    # Custom post editor UI (outside Django admin to avoid route collision)
    path('cms/posts/new/', blog_views.PostEditorView.as_view(), name='post_new'),
    path('cms/posts/<int:post_id>/edit/', blog_views.PostEditorView.as_view(), name='post_edit'),
    path('cms/uploads/images/', blog_views.EditorImageUploadView.as_view(), name='editor_image_upload'),
    path('cms/bots/', blog_views.CmsBotListView.as_view(), name='cms_bots'),
    path('cms/bots/update/', blog_views.CmsBotUpdateView.as_view(), name='cms_bots_update'),
    path('cms/payments/', blog_views.CmsPaymentListView.as_view(), name='cms_payments'),
    path('cms/payments/update-status/', blog_views.CmsPaymentUpdateStatusView.as_view(), name='cms_payments_update_status'),
    path('cms/payments/update-bot/', blog_views.CmsPaymentUpdateBotView.as_view(), name='cms_payments_update_bot'),
    path('cms/payments/create-bot/', blog_views.CmsPaymentCreateBotView.as_view(), name='cms_payments_create_bot'),
    path('cms/payments/delete/', blog_views.CmsPaymentDeleteView.as_view(), name='cms_payments_delete'),
    path('cms/comments/', blog_views.CmsCommentModerationView.as_view(), name='cms_comments'),
    path('cms/comments/approve/', blog_views.CmsCommentApproveView.as_view(), name='cms_comments_approve'),
    path('cms/comments/reject/', blog_views.CmsCommentRejectView.as_view(), name='cms_comments_reject'),
    path('cms/comments/delete/', blog_views.CmsCommentDeleteView.as_view(), name='cms_comments_delete'),
    path('pricing/', PricingPageView.as_view(), name='pricing'),
    path('pricing/assignments/', TemplateView.as_view(template_name='pricing_assignments.html'), name='pricing_assignments'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('signup/', SignupPageView.as_view(), name='signup'),
    path('profile/', ProfilePageView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Password reset flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html',
        email_template_name='auth/password_reset_email.txt',
        subject_template_name='auth/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # SEO files
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml'), name='sitemap'),
    
    # Google Search Console Verification
    path('google61efa2e5a317b80d.html', TemplateView.as_view(template_name='google61efa2e5a317b80d.html', content_type='text/html'), name='google_verification'),
    
    # Analytics
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
