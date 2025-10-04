# 🚀 Quick Deployment Checklist

**For:** https://krixx.pythonanywhere.com  
**Time Required:** ~30 minutes

---

## ⚡ **Quick Steps**

### **1. Update Code** (5 min)
```bash
cd ~/AI_Services
git pull origin main
pip install -r requirements.txt
```

### **2. Update WSGI File** (10 min)
**Location:** Web tab → WSGI configuration file

**Add these lines BEFORE `# 2️⃣ Add your project path`:**

```python
# 🔐 Paystack API Keys (GET FROM: https://dashboard.paystack.com/#/settings/developer)
os.environ['PAYSTACK_PUBLIC_KEY'] = 'YOUR_PAYSTACK_PUBLIC_KEY_HERE'  # ⬅️ REPLACE
os.environ['PAYSTACK_SECRET_KEY'] = 'YOUR_PAYSTACK_SECRET_KEY_HERE'  # ⬅️ REPLACE
os.environ['PAYSTACK_WEBHOOK_SECRET'] = 'YOUR_WEBHOOK_SECRET_HERE'  # ⬅️ REPLACE
os.environ['PAYSTACK_ALLOWED_CURRENCIES'] = 'NGN'

# Security for production
os.environ['SECURE_SSL_REDIRECT'] = 'True'
os.environ['SESSION_COOKIE_SECURE'] = 'True'
os.environ['CSRF_COOKIE_SECURE'] = 'True'
```

### **3. Static Files** (2 min)
```bash
python manage.py collectstatic --noinput
```

### **4. Database** (3 min)
```bash
python manage.py migrate
python manage.py createsuperuser  # If first time
python manage.py seed_demo
```

### **5. Reload** (1 min)
**Web tab → Click "Reload" button**

---

## 🔑 **Where to Get Keys**

### **Paystack Keys:**
1. Login: https://dashboard.paystack.com/
2. Go to: Settings → Developer/API
3. Copy:
   - Public Key (starts with `pk_test_...` or `pk_live_...`)
   - Secret Key (starts with `sk_test_...` or `sk_live_...`)

### **Webhook Secret:**
1. Same page: Settings → Developer/API → Webhooks
2. Add webhook URL: `https://krixx.pythonanywhere.com/api/payments/webhook/`
3. Copy webhook secret

---

## ✅ **Quick Test**

1. Visit: https://krixx.pythonanywhere.com/
2. Click: "See Live Demo →"
3. Test: User registration
4. Test: Test payment (use test card below)

**Paystack Test Card:**
- Card: `4084084084084081`
- Expiry: `12/30`
- CVV: `408`
- OTP: `123456`

---

## 🐛 **Quick Fixes**

### **CSS not loading?**
```bash
python manage.py collectstatic --noinput --clear
```
Then reload web app.

### **500 Error?**
Check **error log** in Web tab.

### **Database error?**
```bash
python manage.py migrate
```

---

## 📁 **Important Files**

| File | Purpose |
|------|---------|
| `wsgi_pythonanywhere.py` | Example WSGI with all configs |
| `PYTHONANYWHERE_DEPLOYMENT.md` | Full deployment guide |
| `requirements.txt` | All dependencies (updated) |

---

## 🎯 **After Deployment**

- [ ] Test homepage
- [ ] Test admin (https://krixx.pythonanywhere.com/admin/)
- [ ] Test demo bot
- [ ] Test payment with test card
- [ ] Check no errors in error log

---

**Need detailed help?** See `PYTHONANYWHERE_DEPLOYMENT.md`

