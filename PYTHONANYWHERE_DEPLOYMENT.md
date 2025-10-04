# PythonAnywhere Deployment Guide for Pi gent

**Last Updated:** October 4, 2025  
**Target:** https://krixx.pythonanywhere.com

---

## 📋 **Prerequisites**

Before deploying, ensure you have:
- ✅ PythonAnywhere account (Free or Paid)
- ✅ Paystack account with API keys
- ✅ Git repository with latest code
- ✅ Database configured on PythonAnywhere

---

## 🚀 **Step-by-Step Deployment**

### **STEP 1: Upload Your Code**

#### **Option A: Using Git (Recommended)**

1. **Open PythonAnywhere Bash Console:**
   - Go to: https://www.pythonanywhere.com/user/krixx/consoles/
   - Click "Bash" to open a new console

2. **Navigate to your project directory:**
   ```bash
   cd ~
   ```

3. **If first time, clone your repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/AI_Services.git
   cd AI_Services
   ```

4. **If updating existing deployment:**
   ```bash
   cd ~/AI_Services
   git pull origin main  # or master, depending on your branch
   ```

#### **Option B: Upload Files Directly**
- Go to: https://www.pythonanywhere.com/user/krixx/files/
- Navigate to `/home/krixx/AI_Services/`
- Upload changed files manually

---

### **STEP 2: Update Requirements**

In the Bash console:

```bash
cd ~/AI_Services

# Activate your virtual environment (if you have one)
source ~/venv/bin/activate  # Adjust path if different

# Or create a new virtual environment
mkvirtualenv --python=python3.10 pigent-env

# Install/update all dependencies
pip install -r requirements.txt

# Verify edge-tts is installed (for blog TTS feature)
pip list | grep edge-tts
```

**Expected output:** `edge-tts    6.1.9` (or similar)

---

### **STEP 3: Configure WSGI File**

1. **Go to Web tab:**
   - Visit: https://www.pythonanywhere.com/user/krixx/webapps/
   - Click on your web app (e.g., `krixx.pythonanywhere.com`)

2. **Find "Code" section**
   - Click on **"WSGI configuration file"** link
   - Example path: `/var/www/krixx_pythonanywhere_com_wsgi.py`

3. **Replace entire file with this:**

```python
import os
import sys

# 1️⃣ Environment variables for Django
os.environ['SECRET_KEY'] = 'j!x12t=gdf48e&=1u)v@$p#g0^w!^!!^e+y98f&+nk$q+p%7x+'
os.environ['DEBUG'] = 'False'

# Host configuration
os.environ['ALLOWED_HOSTS'] = 'krixx.pythonanywhere.com'
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://krixx.pythonanywhere.com'
os.environ['CORS_ALLOWED_ORIGINS'] = 'https://krixx.pythonanywhere.com'

# 🔐 Paystack API Keys
# ⚠️ IMPORTANT: Replace with your ACTUAL keys from https://dashboard.paystack.com/#/settings/developer
os.environ['PAYSTACK_PUBLIC_KEY'] = 'YOUR_PAYSTACK_PUBLIC_KEY_HERE'  # ⬅️ REPLACE
os.environ['PAYSTACK_SECRET_KEY'] = 'YOUR_PAYSTACK_SECRET_KEY_HERE'  # ⬅️ REPLACE
os.environ['PAYSTACK_WEBHOOK_SECRET'] = 'YOUR_WEBHOOK_SECRET_HERE'  # ⬅️ REPLACE

# Currency settings
os.environ['PAYSTACK_ALLOWED_CURRENCIES'] = 'NGN'

# Security settings for production
os.environ['SECURE_SSL_REDIRECT'] = 'True'
os.environ['SESSION_COOKIE_SECURE'] = 'True'
os.environ['CSRF_COOKIE_SECURE'] = 'True'
os.environ['SECURE_HSTS_SECONDS'] = '31536000'
os.environ['SECURE_HSTS_INCLUDE_SUBDOMAINS'] = 'True'
os.environ['SECURE_HSTS_PRELOAD'] = 'True'

# Database configuration (uncomment and configure if using MySQL)
# os.environ['DATABASE_URL'] = 'mysql://krixx:PASSWORD@krixx.mysql.pythonanywhere-services.com/krixx$pigent'

# 2️⃣ Add your project path
path = '/home/krixx/AI_Services'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 3️⃣ Load Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. **Save the file** (Ctrl+S or click "Save")

---

### **STEP 4: Get Your Paystack Keys**

1. **Log in to Paystack:**
   - Visit: https://dashboard.paystack.com/

2. **Go to Settings → Developer/API:**
   - URL: https://dashboard.paystack.com/#/settings/developer

3. **Copy your keys:**
   - **Public Key:** Starts with `pk_test_` (test mode) or `pk_live_` (live mode)
   - **Secret Key:** Starts with `sk_test_` (test mode) or `sk_live_` (live mode)

4. **Get Webhook Secret:**
   - Scroll to "Webhooks" section
   - If not set up yet:
     - Click "Add Webhook"
     - URL: `https://krixx.pythonanywhere.com/api/payments/webhook/`
     - Copy the webhook secret (starts with `whsec_`)

5. **Update WSGI file with these keys** (in Step 3 above)

---

### **STEP 5: Configure Static Files**

1. **In Web tab, find "Static files" section**

2. **Add these mappings:**

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/krixx/AI_Services/staticfiles/` |
| `/media/` | `/home/krixx/AI_Services/media/` |

3. **Collect static files (in Bash console):**
   ```bash
   cd ~/AI_Services
   python manage.py collectstatic --noinput
   ```

---

### **STEP 6: Set Up Database**

#### **Option A: SQLite (Simple, for testing)**
- Django will create `db.sqlite3` automatically
- No configuration needed
- **Not recommended for production**

#### **Option B: MySQL (Recommended for production)**

1. **Create MySQL database:**
   - Go to: https://www.pythonanywhere.com/user/krixx/databases/
   - Note your username: `krixx`
   - Create database: `krixx$pigent`
   - Set a strong password

2. **Update WSGI file with DATABASE_URL:**
   ```python
   os.environ['DATABASE_URL'] = 'mysql://krixx:YOUR_PASSWORD@krixx.mysql.pythonanywhere-services.com/krixx$pigent'
   ```

3. **Run migrations (in Bash console):**
   ```bash
   cd ~/AI_Services
   python manage.py migrate
   ```

---

### **STEP 7: Create Superuser**

```bash
cd ~/AI_Services
python manage.py createsuperuser
```

Follow prompts to create your admin account.

---

### **STEP 8: Seed Demo Bot**

```bash
cd ~/AI_Services
python manage.py seed_demo
```

This creates the demo bot with sample Q&A.

---

### **STEP 9: Set Up Virtual Environment Path**

1. **In Web tab, find "Virtualenv" section**

2. **Enter path to your virtual environment:**
   ```
   /home/krixx/venv/pigent-env
   ```
   (Or wherever you created it in Step 2)

---

### **STEP 10: Reload Your Web App**

1. **Go to Web tab**
2. **Click the big green "Reload" button** at the top
3. **Wait 10-15 seconds for reload to complete**

---

### **STEP 11: Test Your Deployment**

#### **Basic Tests:**

1. **Homepage:**
   - Visit: https://krixx.pythonanywhere.com/
   - Should load with all images and styles

2. **Admin Panel:**
   - Visit: https://krixx.pythonanywhere.com/admin/
   - Log in with superuser credentials

3. **Demo Bot:**
   - Click "See Live Demo →" button
   - Should redirect to Botpress demo bot

4. **Blog:**
   - Visit: https://krixx.pythonanywhere.com/blog/
   - Check text-to-speech feature works

5. **Pricing:**
   - Visit: https://krixx.pythonanywhere.com/pricing/
   - Check Paystack integration (don't complete payment in test mode)

#### **Check Error Logs:**

1. **Go to Web tab**
2. **Find "Log files" section**
3. **Check these logs:**
   - **Error log:** Shows Python errors
   - **Server log:** Shows requests
   - **Access log:** Shows all traffic

---

### **STEP 12: Test Paystack Integration**

1. **Make a test payment:**
   - Go to: https://krixx.pythonanywhere.com/pricing/
   - Select a package
   - Use Paystack test card:
     - **Card Number:** 4084084084084081
     - **Expiry:** Any future date (e.g., 12/30)
     - **CVV:** 408
     - **OTP:** 123456

2. **Verify payment recorded:**
   - Go to admin: https://krixx.pythonanywhere.com/admin/payments/paymenttransaction/
   - Should see test payment

3. **Check webhook:**
   - Go to Paystack dashboard → Settings → Developer/API → Webhooks
   - Click on your webhook
   - Should see successful deliveries

---

## 🔄 **Updating After Changes**

### **Quick Update (No dependency changes):**

```bash
# 1. Pull latest code
cd ~/AI_Services
git pull origin main

# 2. Collect static files (if CSS/JS changed)
python manage.py collectstatic --noinput

# 3. Run migrations (if models changed)
python manage.py migrate

# 4. Reload web app
# Go to Web tab and click "Reload"
```

### **Full Update (With new dependencies):**

```bash
# 1. Pull latest code
cd ~/AI_Services
git pull origin main

# 2. Update dependencies
pip install -r requirements.txt --upgrade

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Run migrations
python manage.py migrate

# 5. Reload web app
# Go to Web tab and click "Reload"
```

---

## 🐛 **Troubleshooting**

### **Issue: Site shows "Something went wrong :-("**

**Solution:**
1. Check error log in Web tab
2. Look for Python errors
3. Common issues:
   - Missing environment variable
   - Database connection error
   - Static files not collected

### **Issue: Static files (CSS/JS/images) not loading**

**Solution:**
```bash
cd ~/AI_Services
python manage.py collectstatic --noinput --clear
```
Then reload web app.

### **Issue: "DisallowedHost at /" error**

**Solution:**
- Check `ALLOWED_HOSTS` in WSGI file
- Ensure it matches your domain exactly
- Reload web app after changes

### **Issue: Paystack payments not working**

**Solution:**
1. Verify API keys are correct in WSGI file
2. Check Paystack dashboard for errors
3. Ensure webhook URL is correct:
   - `https://krixx.pythonanywhere.com/api/payments/webhook/`
4. Test with Paystack test card (see Step 12)

### **Issue: Database errors**

**Solution:**
```bash
cd ~/AI_Services
python manage.py migrate
```

### **Issue: "Import Error" or "Module not found"**

**Solution:**
```bash
# Reinstall dependencies
cd ~/AI_Services
pip install -r requirements.txt --force-reinstall
```

---

## 📊 **Monitoring & Maintenance**

### **Daily Checks:**
- ✅ Check error logs for issues
- ✅ Monitor payment transactions in admin
- ✅ Verify demo bot is working

### **Weekly Tasks:**
- ✅ Backup database
- ✅ Review and moderate blog comments
- ✅ Check Paystack dashboard for successful payments
- ✅ Update content (blog posts, reviews)

### **Monthly Tasks:**
- ✅ Update dependencies: `pip install -r requirements.txt --upgrade`
- ✅ Review security settings
- ✅ Check for Django security updates
- ✅ Optimize database (if needed)

---

## 🔐 **Security Best Practices**

### **1. Keep Secrets Secret:**
- ✅ Never commit API keys to Git
- ✅ Use environment variables in WSGI file
- ✅ Rotate secrets regularly

### **2. Use HTTPS Everywhere:**
- ✅ Force SSL redirect (enabled in WSGI)
- ✅ Secure cookies (enabled in WSGI)
- ✅ HSTS enabled (enabled in WSGI)

### **3. Database Security:**
- ✅ Use strong database password
- ✅ Regular backups
- ✅ Limit database access

### **4. Monitor for Attacks:**
- ✅ Check access logs regularly
- ✅ Set up Sentry for error tracking (optional)
- ✅ Enable rate limiting (if needed)

---

## 📞 **Support Resources**

### **PythonAnywhere:**
- **Help:** https://help.pythonanywhere.com/
- **Forums:** https://www.pythonanywhere.com/forums/
- **Support:** help@pythonanywhere.com

### **Django:**
- **Docs:** https://docs.djangoproject.com/
- **Deployment:** https://docs.djangoproject.com/en/5.0/howto/deployment/

### **Paystack:**
- **Docs:** https://paystack.com/docs/
- **Support:** support@paystack.com
- **Status:** https://status.paystack.com/

---

## ✅ **Post-Deployment Checklist**

After completing all steps:

- [ ] Website loads at https://krixx.pythonanywhere.com/
- [ ] All static files (CSS/JS/images) working
- [ ] Admin panel accessible
- [ ] Demo bot redirects properly
- [ ] Blog posts display correctly
- [ ] Text-to-speech works on blog posts
- [ ] Pricing page loads
- [ ] Test payment completes successfully
- [ ] Paystack webhook receives events
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard shows user info
- [ ] Portfolio page loads
- [ ] Botpress chat widget appears
- [ ] Custom CTA button shows
- [ ] Social media links work
- [ ] No errors in error log
- [ ] HTTPS enforced (no insecure warnings)

---

## 🎉 **You're Live!**

Your Pi gent website is now deployed on PythonAnywhere!

**Next Steps:**
1. Share your link: https://krixx.pythonanywhere.com/
2. Test all features thoroughly
3. Create your first blog post
4. Monitor for any issues
5. Start marketing your service!

**Questions?** Check the troubleshooting section or contact PythonAnywhere support.

---

**Deployed by:** Krixx Valentine  
**Deployment Date:** October 2025  
**Platform:** PythonAnywhere  
**Domain:** https://krixx.pythonanywhere.com

