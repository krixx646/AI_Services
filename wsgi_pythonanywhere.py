import os
import sys

# 1️⃣ Environment variables for Django
# ⚠️ SECURITY: Keep these values secret!
os.environ['SECRET_KEY'] = 'j!x12t=gdf48e&=1u)v@$p#g0^w!^!!^e+y98f&+nk$q+p%7x+'
os.environ['DEBUG'] = 'False'

# Host configuration
os.environ['ALLOWED_HOSTS'] = 'krixx.pythonanywhere.com'
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://krixx.pythonanywhere.com'
os.environ['CORS_ALLOWED_ORIGINS'] = 'https://krixx.pythonanywhere.com'

# 🔐 Paystack API Keys
# ⚠️ IMPORTANT: Replace these with your ACTUAL Paystack keys!
# Get them from: https://dashboard.paystack.com/#/settings/developer
os.environ['PAYSTACK_PUBLIC_KEY'] = 'pk_test_YOUR_PUBLIC_KEY_HERE'  # ⬅️ REPLACE THIS
os.environ['PAYSTACK_SECRET_KEY'] = 'sk_test_YOUR_SECRET_KEY_HERE'  # ⬅️ REPLACE THIS
os.environ['PAYSTACK_WEBHOOK_SECRET'] = 'YOUR_WEBHOOK_SECRET_HERE'  # ⬅️ REPLACE THIS

# Currency settings
os.environ['PAYSTACK_ALLOWED_CURRENCIES'] = 'NGN'  # Can add USD when ready: 'NGN,USD'

# Email configuration (optional - for production emails)
# os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
# os.environ['EMAIL_HOST'] = 'smtp.gmail.com'
# os.environ['EMAIL_PORT'] = '587'
# os.environ['EMAIL_USE_TLS'] = 'True'
# os.environ['EMAIL_HOST_USER'] = 'your-email@gmail.com'
# os.environ['EMAIL_HOST_PASSWORD'] = 'your-app-password'
# os.environ['DEFAULT_FROM_EMAIL'] = 'Pi gent <noreply@krixx.pythonanywhere.com>'

# Security settings for production
os.environ['SECURE_SSL_REDIRECT'] = 'True'
os.environ['SESSION_COOKIE_SECURE'] = 'True'
os.environ['CSRF_COOKIE_SECURE'] = 'True'
os.environ['SECURE_HSTS_SECONDS'] = '31536000'  # 1 year
os.environ['SECURE_HSTS_INCLUDE_SUBDOMAINS'] = 'True'
os.environ['SECURE_HSTS_PRELOAD'] = 'True'

# Database configuration (MySQL on PythonAnywhere)
# Format: mysql://username:password@hostname/database_name
# os.environ['DATABASE_URL'] = 'mysql://krixx:YOUR_DB_PASSWORD@krixx.mysql.pythonanywhere-services.com/krixx$pigent'

# Optional: Sentry error tracking
# os.environ['SENTRY_DSN'] = 'your-sentry-dsn-here'
# os.environ['SENTRY_ENVIRONMENT'] = 'production'

# 2️⃣ Add your project path
path = '/home/krixx/AI_Services'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 3️⃣ Load Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

