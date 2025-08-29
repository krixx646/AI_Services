## Developer Tooling

Install optional dev tools in your environment:

```bash
pip install drf-spectacular black isort coverage
```

Format and sort imports:

```bash
black .
isort .
```

Generate API schema and open docs:

```bash
# Schema JSON
curl http://localhost:8000/api/schema/ -o openapi.json
# Swagger UI
start http://localhost:8000/api/docs/
# Redoc
start http://localhost:8000/api/redoc/
```

Run coverage (example using Django's test runner):

```bash
coverage run manage.py test
coverage report -m
coverage html  # outputs to htmlcov/index.html
```

## Deploying on PythonAnywhere (free plan)

1) Prepare env vars in `.env` on PythonAnywhere:
```
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com
CORS_ALLOWED_ORIGINS=https://yourusername.pythonanywhere.com
SECRET_KEY=<paste_generated_key>
PAYSTACK_PUBLIC_KEY=pk_test_xxx
PAYSTACK_SECRET_KEY=sk_test_xxx
PAYSTACK_ALLOWED_CURRENCIES=NGN,USD
```

2) Install deps and collect static:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

3) In Web tab → Manual config:
- WSGI module: `core.wsgi`
- Virtualenv: your venv path
- Static: URL `/static/` → path `/home/<user>/AI_Services/staticfiles`

4) Reload the web app.

---

## Live deployment

- Base site: https://krixx.pythonanywhere.com/ ([link](https://krixx.pythonanywhere.com/))
- API docs:
  - Swagger UI: https://krixx.pythonanywhere.com/api/docs/ ([link](https://krixx.pythonanywhere.com/api/docs/))
  - Redoc: https://krixx.pythonanywhere.com/api/redoc/ ([link](https://krixx.pythonanywhere.com/api/redoc/))

Base API URL: `https://krixx.pythonanywhere.com` (append the paths below)

## API quickstart

### Authentication (JWT tokens)
- Register: `POST /api/accounts/register/`
- Login: `POST /api/accounts/login/` → returns `{ access, refresh }`

Example:
```bash
curl -X POST https://krixx.pythonanywhere.com/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"yourpass"}'
```

Use `Authorization: Bearer <access>` for authenticated requests.

### Accounts
- `POST /api/accounts/register/`
- `POST /api/accounts/login/`
- `GET|PUT|PATCH|DELETE /api/accounts/profile/{id}/`

### Payments (Paystack)
- `POST /api/payments/init/` (auth): body `{ amount, currency }`
  - Amount must be in whole units on our side; we send smallest units to Paystack (x100).
  - Currency must be enabled on your Paystack account (default allowed: NGN, USD).
- `POST /api/payments/webhook/` (Paystack → server): set the webhook URL in your dashboard to this endpoint.
- `GET /api/payments/verify/{reference}/` (auth): double-check a transaction.

Notes:
- Use TEST keys for staging: `PAYSTACK_SECRET_KEY=sk_test_...`, optionally `PAYSTACK_PUBLIC_KEY=pk_test_...` if you later use Inline.
- Webhook signature is verified via `X-Paystack-Signature` using your Secret Key (HMAC-SHA512).

### Bots Q&A
- `GET /api/bots/{reference}/questions/`
- `POST /api/bots/{reference}/answer/` → body `{ "question_id" }` or `{ "text" }`

### Reviews
- `GET /api/bots/reviews/?bot={id}`
- `POST /api/bots/reviews/` (auth)
- `GET|PUT|PATCH|DELETE /api/bots/reviews/{id}/` (auth; owner/admin)

### Blog
- Posts: `GET|POST /api/blog/posts/`, `GET|PUT|PATCH|DELETE /api/blog/posts/{id}/`
- Retrieve by slug: `GET /api/blog/posts/by-slug/{slug}/`
- Categories: `GET|POST /api/blog/categories/`, `GET|PUT|PATCH|DELETE /api/blog/categories/{id}/`
- Tags: `GET|POST /api/blog/tags/`, `GET|PUT|PATCH|DELETE /api/blog/tags/{id}/`
- Comments: `GET|POST /api/blog/posts/{post_id}/comments/` (default lists approved)
- Comment detail (owner/mod): `GET|PATCH|DELETE /api/blog/comments/{id}/`
- Moderate (admin): `POST /api/blog/comments/{id}/moderate/` `{ "action": "approve"|"reject" }`

### Demo
- `GET /api/demo/info/` → `{ reference, status, bot_url }`

### Global search
- `GET /api/search/?q=keyword&type=posts|bots|reviews|all`

## Environment variables (summary)

Minimal production set:
```
DEBUG=False
ALLOWED_HOSTS=youruser.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://youruser.pythonanywhere.com
CORS_ALLOWED_ORIGINS=https://youruser.pythonanywhere.com
SECRET_KEY=<generated>
```

Database (PythonAnywhere MySQL):
```
DATABASE_URL=mysql://USER:PASS@USER.mysql.pythonanywhere-services.com/USER$default?charset=utf8mb4
```

Payments (optional in staging):
```
PAYSTACK_SECRET_KEY=sk_test_...
PAYSTACK_PUBLIC_KEY=pk_test_...
PAYSTACK_ALLOWED_CURRENCIES=NGN,USD
```

Moderation:
```
AUTO_APPROVE_COMMENTS=False
```

## Admin & moderation
- Use Django admin at `/admin/` to manage posts, comments (approve/reject), bots, and payments.
- Comments default to pending unless `AUTO_APPROVE_COMMENTS=True`.

## CORS/CSRF when splitting frontend
- If you host a separate frontend (Netlify/Vercel/etc.), add that origin to `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`.

## Tests
```bash
python manage.py test
```

