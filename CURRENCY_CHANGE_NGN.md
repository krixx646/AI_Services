# Currency Update: USD → NGN (Naira)

## Summary
Changed the default currency from USD to NGN (Nigerian Naira) across the entire payment system. USD can be re-enabled in the future by updating the `.env` file.

## Changes Made

### 1. Database Model (`payments/models.py`)
```python
# Before:
currency = models.CharField(max_length=8, default="USD")

# After:
currency = models.CharField(max_length=8, default="NGN")
```
- All new payments will default to NGN
- Existing payments retain their original currency (backward compatible)

### 2. Admin Payment Dashboard (`blog/views.py`)
```python
# Before:
'currency': 'USD',

# After:
'currency': 'NGN',
```
- Statistics summary now displays "NGN" instead of "USD"
- Total amounts show in Naira

### 3. Settings Configuration (`core/settings.py`)
```python
_allowed_currencies = os.environ.get('PAYSTACK_ALLOWED_CURRENCIES', 'NGN')
PAYSTACK_ALLOWED_CURRENCIES = [c.strip().upper() for c in _allowed_currencies.split(',') if c.strip()]
```
- Default: **NGN only**
- Already correctly configured (no changes needed)

### 4. Frontend Pricing Page (`templates/pricing.html`)
- Already supports both NGN and USD
- Automatically shows NGN-only for Nigerian users
- Currency toggle hides USD option when not in `PAYSTACK_ALLOWED_CURRENCIES`

## How to Re-Enable USD in the Future

### Step 1: Update `.env` file
Add or modify:
```env
PAYSTACK_ALLOWED_CURRENCIES=NGN,USD
```

### Step 2: Restart the server
```bash
python manage.py runserver
```

### Step 3: Verify
- Visit `/pricing/`
- Currency toggle should show both Naira (₦) and USD ($)
- Nigerian users see NGN by default
- International users see USD by default

## Current Behavior

### For Nigerian Users:
- ✅ See Naira (₦) prices only
- ✅ No currency toggle (NGN-only mode)
- ✅ Paystack processes in NGN

### For International Users:
- ✅ See Naira (₦) prices only (until USD is re-enabled)
- ✅ Can still pay in NGN via Paystack
- ⏳ USD option will appear once enabled in `.env`

## Payment Dashboard Display

Admin payment management dashboard now shows:
- **Total Success**: X NGN
- **Pending**: X NGN
- All payment amounts displayed in NGN

## Pricing Catalog

Currently active prices (from `core/settings.py`):

### NGN (Active)
- Trial (1-3 pages): ₦2,000
- Starter (≤60 pages): ₦10,000
- Standard (61-120 pages): ₦14,999
- Extended (121-200 pages): ₦19,000
- Single Course: ₦10,000
- Bundle (6 courses): ₦50,000

### USD (Inactive, can be enabled)
- Trial: $10
- Starter: $29
- Standard: $49
- Extended: $69
- Single Course: $30
- Bundle: $160

## No Data Migration Required

Since we only changed the **default** value:
- ✅ Existing USD payments remain as USD in the database
- ✅ New payments automatically use NGN
- ✅ No risk of data corruption
- ✅ Backward compatible

## Testing Checklist

### ✅ Completed:
- [x] Database model updated
- [x] Admin dashboard displays NGN
- [x] New payments default to NGN
- [x] Pricing page already supports NGN-first

### To Test:
- [ ] Create a new test payment (verify it uses NGN)
- [ ] Check admin payment dashboard (verify stats show NGN)
- [ ] View receipt page (verify currency display)
- [ ] Test Paystack checkout (verify NGN is used)

## Notes

- **Paystack** natively supports both NGN and USD
- The pricing page automatically handles currency conversion display
- Server-side validation ensures only allowed currencies are accepted
- Currency geolocation logic is already in place (`core/views.py`)

