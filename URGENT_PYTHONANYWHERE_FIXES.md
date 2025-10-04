# 🚨 URGENT: PythonAnywhere Fixes

**Based on your error logs from October 4, 2025**

---

## ❗ **CRITICAL: Fix WSGI Syntax Error FIRST**

### **Error:**
```
SyntaxError: invalid syntax
Line 93: os.environ['PAYSTACK_WEBHOOK_SECRET'] =
```

### **Fix:**
1. **Go to PythonAnywhere Web tab**
2. **Click WSGI configuration file**
3. **Find line ~93** (the `PAYSTACK_WEBHOOK_SECRET` line)
4. **It currently looks like:**
   ```python
   os.environ['PAYSTACK_WEBHOOK_SECRET'] =   # ❌ BROKEN!
   ```

5. **Change it to (leave empty if not using webhooks):**
   ```python
   os.environ['PAYSTACK_WEBHOOK_SECRET'] = ''  # Empty is fine!
   ```

   **Note:** Webhooks are optional. You can use Paystack without them. Only set this if you explicitly configured webhooks in Paystack dashboard.

7. **Save file** (Ctrl+S)
8. **Reload web app** (green button at top)

**Your site will work again after this fix!**

---

## ✅ **Other Fixes (Update your local code)**

### **1. robots.txt - Stop 404 Errors**

I've created `templates/robots.txt` - push this to your repo and pull on PythonAnywhere.

Then run on PythonAnywhere:
```bash
cd ~/AI_Services
git pull origin main
python manage.py collectstatic --noinput
```

Reload web app.

---

### **2. favicon.ico - Added**

I've added favicon link to `templates/base.html` - it now uses your `pigent.png` as favicon.

Push and pull as above.

---

### **3. Portfolio Template Error**

**Error:**
```
TemplateSyntaxError: Invalid template name in 'extends' tag: ''. Got this from the 'base.html' variable.
```

**This happens when:** Someone visits `/portfolio/` page

**Check on PythonAnywhere:**
```bash
cd ~/AI_Services
cat portfolio/templates/portfolio/index.html | head -5
```

**First line should be:**
```django
{% extends 'base.html' %}
```

**NOT:**
```django
{% extends base.html %}  # ❌ Missing quotes
```

---

## 📋 **Quick Deployment Steps**

### **ON PYTHONANYWHERE:**

```bash
# 1. Go to Bash console
cd ~/AI_Services

# 2. Pull latest code
git pull origin main

# 3. Install any new dependencies
pip install -r requirements.txt

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Run migrations (if any)
python manage.py migrate

# 6. Reload web app
# Go to Web tab and click "Reload"
```

---

## 🔍 **Verify Fixes**

After fixes, test:
1. ✅ Homepage loads: https://krixx.pythonanywhere.com/
2. ✅ No WSGI error in error log
3. ✅ `/robots.txt` works: https://krixx.pythonanywhere.com/robots.txt
4. ✅ Favicon appears in browser tab
5. ✅ Portfolio works: https://krixx.pythonanywhere.com/portfolio/
6. ✅ Demo bot redirects: https://krixx.pythonanywhere.com/api/demo/info/

---

## 📊 **Your Error Log Summary**

### **What Was Wrong:**
- ❌ WSGI file syntax error (line 93) - **CRITICAL**
- ❌ Missing `robots.txt` - causing 404s
- ❌ Missing favicon - causing 404s  
- ❌ Portfolio template error
- ⚠️ DRF serializer warnings (harmless, can ignore)

### **What I Fixed:**
- ✅ Added `robots.txt` file
- ✅ Added favicon link in base template
- ✅ Updated `core/urls.py` to serve robots.txt

### **What YOU Need to Do:**
1. **Fix WSGI line 93** (add value to webhook secret)
2. **Push/pull latest code**
3. **Reload web app**

---

## 🆘 **If Site Still Down**

### **Check Error Log:**
1. Go to Web tab
2. Scroll to "Log files"
3. Click on "Error log"
4. Look for the LATEST error (bottom of file)
5. Send me the error message

### **Common Issues:**

**Issue: "No module named 'edge_tts'"**
```bash
cd ~/AI_Services
source ~/venv/bin/activate  # or wherever your venv is
pip install edge-tts
```

**Issue: Static files not loading**
```bash
python manage.py collectstatic --noinput --clear
```

**Issue: Database errors**
```bash
python manage.py migrate
```

---

## ✨ **After Everything Works**

### **Set Up Paystack Properly:**

1. **Get your Paystack keys:**
   - Login: https://dashboard.paystack.com/
   - Go to: Settings → Developer/API
   - Copy:
     - Public Key (starts with `pk_test_` or `pk_live_`)
     - Secret Key (starts with `sk_test_` or `sk_live_`)

2. **Update WSGI file with real keys:**
   ```python
   os.environ['PAYSTACK_PUBLIC_KEY'] = 'pk_test_YOUR_REAL_KEY'
   os.environ['PAYSTACK_SECRET_KEY'] = 'sk_test_YOUR_REAL_KEY'
   os.environ['PAYSTACK_WEBHOOK_SECRET'] = ''  # Leave empty (webhooks optional)
   ```

3. **Set up webhook (OPTIONAL - for automatic payment confirmation):**
   - Only if you want automatic payment notifications
   - Same page, go to Webhooks section
   - Add webhook URL: `https://krixx.pythonanywhere.com/api/payments/webhook/`
   - Copy webhook secret and update WSGI file
   - **Note:** Your site works fine WITHOUT webhooks!

4. **Reload web app**

---

## 📞 **Need Help?**

If you get stuck:
1. Check error log for specific error message
2. Google the error message
3. Check PythonAnywhere help: https://help.pythonanywhere.com/
4. Ask me with the specific error message

---

**Priority Order:**
1. 🔴 **CRITICAL:** Fix WSGI line 93 (5 minutes)
2. 🟡 **Important:** Pull latest code (10 minutes)
3. 🟢 **Optional:** Set up real Paystack keys (15 minutes)

**Total time to fix: ~30 minutes**

Good luck! 🚀

