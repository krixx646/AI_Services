# Demo Bot Setup Guide

## Overview
Your Pi gent website now has a live demo bot powered by Botpress, showcasing the capabilities of your AI Study Agent service.

---

## 📍 **Demo Bot Access Points**

### **1. Direct Link:**
- **URL:** `/api/demo/info/`
- **Redirects to:** Live Botpress demo bot in a new tab
- **Best for:** Visitors who want to quickly try the demo

### **2. Homepage CTA:**
- **Button:** "See Live Demo →" on the hero section
- **Button:** "Try the Demo Agent Trained on These Notes" below the handwritten carousel
- **Action:** Opens demo bot in a new window

### **3. Footer Link:**
- **Link:** "Demo bot info" in the footer
- **Available on:** All pages
- **Action:** Redirects to live demo

---

## 🔗 **Demo Bot URL**

```
https://cdn.botpress.cloud/webchat/v3.3/shareable.html?configUrl=https://files.bpcontent.cloud/2025/10/02/13/20251002132027-GSNRC2QE.json
```

This is your **shareable Botpress demo bot** that visitors can interact with to see how your AI agents work.

---

## 🛠️ **How It Works**

### **User Flow:**
1. Visitor clicks "See Live Demo" button
2. System redirects to `/api/demo/info/`
3. Django view redirects to the Botpress shareable URL
4. Demo bot opens in a new tab/window
5. Visitor can interact with the bot to see capabilities

### **API Endpoints:**

#### **`GET /api/demo/info/`** (Primary)
- **Type:** Django redirect view
- **Returns:** 302 redirect to Botpress shareable URL
- **Purpose:** Direct visitors to the live demo

#### **`GET /api/demo/data/`** (Legacy/API)
- **Type:** REST API endpoint
- **Returns:** JSON with demo bot details
```json
{
  "reference": "demo-bot",
  "status": "ready",
  "bot_url": "https://cdn.botpress.cloud/webchat/v3.3/shareable.html?configUrl=..."
}
```
- **Purpose:** For API consumers or future integrations

---

## 📝 **Files Modified**

### **1. `demo/views.py`**
```python
class DemoInfoView(View):
    """Redirect to the live demo bot"""
    def get(self, request):
        demo_url = "https://cdn.botpress.cloud/webchat/v3.3/shareable.html?configUrl=..."
        return redirect(demo_url)
```

### **2. `demo/urls.py`**
```python
urlpatterns = [
    path('info/', views.DemoInfoView.as_view(), name='demo-info'),
    path('data/', views.DemoInfoAPIView.as_view(), name='demo-info-api'),
]
```

### **3. `demo/management/commands/seed_demo.py`**
- Updated bot_url to use the Botpress shareable link
- Run `python manage.py seed_demo` to create/update demo bot in database

---

## 🎨 **Customizing the Demo Bot**

### **Update the Demo Bot URL:**
If you create a new Botpress bot or update the configuration:

1. **Get new shareable link** from Botpress dashboard
2. **Update in 3 places:**
   - `demo/views.py` → `DemoInfoView` (line 12)
   - `demo/views.py` → `DemoInfoAPIView` (line 24)
   - `demo/management/commands/seed_demo.py` (line 22)

3. **Run migration:**
   ```bash
   python manage.py seed_demo
   ```

### **Change Button Text:**
Update in `templates/index.html`:
- Line ~12: "See Live Demo →"
- Line ~208: "Try the Demo Agent Trained on These Notes"

---

## 🧪 **Testing the Demo Bot**

### **1. Test Direct Access:**
```bash
curl -I http://localhost:8000/api/demo/info/
# Should return 302 redirect to Botpress URL
```

### **2. Test API Endpoint:**
```bash
curl http://localhost:8000/api/demo/data/
# Should return JSON with bot details
```

### **3. Test from Browser:**
1. Visit your homepage
2. Click "See Live Demo →" button
3. Demo bot should open in new tab
4. Interact with the bot to test responses

---

## 📊 **Demo Bot Features to Showcase**

Your demo bot should demonstrate:
- ✅ **Quick responses** to course-related questions
- ✅ **Accurate information** from lecture notes
- ✅ **Natural conversation** flow
- ✅ **ITK Mode** (if enabled) - combining notes with latest context
- ✅ **Study tips** and exam preparation advice

---

## 🔄 **Updating Demo Content**

To update what the demo bot knows:
1. Log in to your **Botpress Cloud** dashboard
2. Navigate to your demo bot
3. Update the **Knowledge Base** with new content
4. Train the bot
5. Test and publish
6. No code changes needed! The shareable link stays the same.

---

## 🚀 **Production Deployment**

### **Before Launch:**
1. ✅ Test demo bot thoroughly
2. ✅ Verify all links work
3. ✅ Check mobile responsiveness
4. ✅ Ensure demo bot is trained with relevant content
5. ✅ Add tracking/analytics to measure demo usage

### **Monitoring:**
- Track clicks on "See Live Demo" buttons
- Monitor demo bot engagement in Botpress analytics
- Measure conversion from demo → pricing page

---

## 🎯 **Best Practices**

### **Demo Bot Content:**
- Keep responses **short and engaging**
- Showcase **real value** (not just "hello, how can I help?")
- Include **call-to-action** to create their own agent
- Add **pricing information** when asked
- Mention **fast turnaround times** (6-48 hours)

### **User Experience:**
- Demo should **load quickly** (< 3 seconds)
- Bot should **respond instantly** (Botpress handles this)
- Include **sample questions** users can ask
- Make it **obvious** this is a demo, not their personal agent

---

## 📞 **Support**

If the demo bot isn't working:
1. Check Botpress dashboard for bot status
2. Verify the shareable URL is still valid
3. Test the `/api/demo/info/` endpoint
4. Check browser console for errors
5. Contact Botpress support if bot is down

---

## 🔗 **Related Documentation**

- [Botpress Documentation](https://botpress.com/docs)
- [Webchat Configuration](https://botpress.com/docs/webchat/get-started/configure-your-webchat)
- [FAQ.md](./FAQ.md) - Includes demo bot info for users
- [README.md](./README.md) - Overall project documentation

---

**Last Updated:** October 4, 2025  
**Demo Bot URL Valid Until:** Check Botpress dashboard for expiration  
**Version:** 1.0

