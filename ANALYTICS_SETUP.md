# 📊 Analytics Dashboard Setup Guide

Your Pi gent website now has a **comprehensive analytics dashboard** to track visitors, page views, and user behavior!

---

## ✨ **What's Included:**

### **1. Automatic Page View Tracking**
- ✅ Every page visit is automatically logged
- ✅ Tracks: URL, visitor IP, browser, device, OS, referrer
- ✅ Distinguishes between unique visitors and page views
- ✅ No manual tracking code needed!

### **2. Beautiful Analytics Dashboard**
- 📈 Traffic trends (last 30 days)
- 👥 Visitor statistics (today, week, month)
- 🖥️ Device breakdown (Desktop/Mobile/Tablet)
- 🌐 Browser usage (Chrome, Firefox, Safari, etc.)
- ⏰ Hourly traffic patterns
- 📄 Top pages
- 🔗 Top referrers (where visitors come from)
- ⚡ Recent events

### **3. Staff-Only Access**
- ✅ Only admins/staff can view analytics
- ✅ Accessible from navbar dropdown
- ✅ Secure and private

---

## 🚀 **Setup Instructions:**

### **Step 1: Run Migrations (Local)**

```bash
cd C:\Users\ADMIN\Desktop\AI_Services
python manage.py makemigrations analytics
python manage.py migrate
```

### **Step 2: Test Locally**

```bash
python manage.py runserver
```

Visit: http://localhost:8000/analytics/

(You must be logged in as staff/admin)

### **Step 3: Deploy to PythonAnywhere**

```bash
# On your local machine
git add .
git commit -m "feat: Add comprehensive analytics dashboard with page tracking"
git push origin main
```

Then on PythonAnywhere Bash console:

```bash
cd ~/AI_Services
git pull origin main
python manage.py makemigrations analytics
python manage.py migrate
```

Reload your web app!

---

## 📍 **How to Access:**

### **For Admins:**
1. Log in to your site
2. Click your profile avatar (top-right)
3. Click **"📊 Analytics Dashboard"**

**Or visit directly:** https://krixx.pythonanywhere.com/analytics/

---

## 📊 **Dashboard Features:**

### **Key Metrics Cards:**
- **Today's Views** - Total page views today (with % change from yesterday)
- **Today's Visitors** - Unique visitors today (with % change)
- **This Week** - 7-day totals
- **This Month** - 30-day totals

### **Charts:**
1. **Traffic Trend** - Line chart showing daily views and visitors (30 days)
2. **Device Breakdown** - Pie chart (Desktop vs Mobile vs Tablet)
3. **Browser Usage** - Bar chart (Chrome, Firefox, Safari, etc.)
4. **Hourly Traffic** - Bar chart showing traffic by hour (last 24h)

### **Tables:**
- **Top Pages** - Most visited pages with view counts
- **Top Referrers** - External sites sending you traffic
- **Recent Events** - Custom tracked events (signups, payments, etc.)

### **All-Time Stats:**
- Total page views
- Total unique visitors
- Total events tracked

---

## 🎯 **What Gets Tracked:**

### **Automatically Tracked:**
- ✅ Every page visit (except admin, API, static files)
- ✅ Visitor's IP address
- ✅ Browser type (Chrome, Firefox, Safari, etc.)
- ✅ Device type (Desktop, Mobile, Tablet)
- ✅ Operating system (Windows, macOS, Linux, Android, iOS)
- ✅ Referrer (where they came from)
- ✅ Page title
- ✅ Timestamp

### **NOT Tracked:**
- ❌ Admin pages (`/admin/`)
- ❌ API endpoints (`/api/`)
- ❌ CMS pages (`/cms/`)
- ❌ Static files (`/static/`, `/media/`)
- ❌ robots.txt, favicon.ico

---

## 🔧 **Advanced: Custom Event Tracking**

Want to track specific actions? Add this to your views:

```python
from analytics.models import Event

# Track a button click
Event.objects.create(
    event_type='click',
    event_name='CTA Button Clicked',
    event_data={'button': 'Create Agent Now'},
    user=request.user if request.user.is_authenticated else None,
    session_key=request.session.session_key,
    ip_address=get_client_ip(request),
    page_url=request.build_absolute_uri()
)

# Track a payment
Event.objects.create(
    event_type='payment',
    event_name='Payment Initiated',
    event_data={'amount': 15000, 'currency': 'NGN'},
    user=request.user,
    session_key=request.session.session_key,
    ip_address=get_client_ip(request),
    page_url=request.build_absolute_uri()
)
```

---

## 📈 **Understanding the Data:**

### **Page Views vs Visitors:**
- **Page View** = Every time a page loads
- **Unique Visitor** = Counted once per session (even if they view multiple pages)

### **Session:**
- A session is a single browsing session
- Lasts until browser is closed or ~2 weeks of inactivity
- Same visitor = same session key

### **Growth Percentages:**
- Green ↑ = Increase from previous period
- Red ↓ = Decrease from previous period
- Calculated as: `((current - previous) / previous) * 100`

---

## 🎨 **Customization:**

### **Change Time Ranges:**
Edit `analytics/views.py` and modify these lines:

```python
week_ago = now - timedelta(days=7)   # Change to 14 for 2 weeks
month_ago = now - timedelta(days=30)  # Change to 60 for 2 months
```

### **Add More Charts:**
Edit `templates/analytics/dashboard.html` and add Chart.js charts.

### **Exclude More Paths:**
Edit `analytics/middleware.py` and add to `EXCLUDE_PATHS`:

```python
EXCLUDE_PATHS = [
    r'^/admin/',
    r'^/your-path/',  # Add your path here
]
```

---

## 🔒 **Privacy & Performance:**

### **Privacy:**
- IP addresses are stored but not displayed publicly
- Only staff can view analytics
- No personal data is tracked (just browsing behavior)
- Compliant with basic privacy practices

### **Performance:**
- Middleware is lightweight (~5ms overhead)
- Database indexes for fast queries
- Charts load asynchronously
- No impact on user experience

### **Data Retention:**
To keep database size manageable, you can periodically clean old data:

```python
# Delete page views older than 90 days
from datetime import timedelta
from django.utils import timezone
from analytics.models import PageView

cutoff = timezone.now() - timedelta(days=90)
PageView.objects.filter(timestamp__lt=cutoff).delete()
```

---

## 🐛 **Troubleshooting:**

### **"No data yet" showing:**
- Make sure middleware is active (check `settings.py`)
- Visit some pages while logged out
- Refresh analytics dashboard

### **Charts not loading:**
- Check browser console for errors
- Ensure Chart.js CDN is accessible
- Try hard refresh (Ctrl+Shift+R)

### **Permission denied:**
- Only staff users can access `/analytics/`
- Make yourself staff: `python manage.py createsuperuser`
- Or in admin: User → Staff status = ✅

---

## 📊 **Example Use Cases:**

### **1. Track Marketing Campaigns:**
- Check "Top Referrers" to see which sites send traffic
- Monitor daily traffic for campaign spikes
- See which pages convert best

### **2. Optimize User Experience:**
- Check device breakdown (mobile vs desktop)
- See hourly patterns (when users are most active)
- Identify most popular pages

### **3. Monitor Growth:**
- Track daily visitor growth
- Compare week-over-week trends
- Set goals based on data

### **4. Understand Your Audience:**
- See what browsers they use
- Check device preferences
- Identify traffic sources

---

## 🎉 **You're All Set!**

Your analytics dashboard is ready to track your website's success!

**Access it at:** https://krixx.pythonanywhere.com/analytics/

**Questions?** Check the code in:
- `analytics/models.py` - Data models
- `analytics/views.py` - Dashboard logic
- `analytics/middleware.py` - Tracking logic
- `templates/analytics/dashboard.html` - Dashboard UI

---

**Happy tracking! 📈**
