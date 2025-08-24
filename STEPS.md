## Build Steps: AI‑Powered Notes‑to‑Chatbot Service

Each step is atomic and should be completed before moving to the next. Do not mix steps. The stack is Django + DRF for the API, with Django templates and static files for the website, Botpress for chatbot demo, and Paystack for payments.

### Step 1: Initialize Project Environment
- Create virtual environment and install core dependencies.
```bash
python -m venv venv
./venv/Scripts/Activate.ps1
pip install django djangorestframework django-cors-headers django-filter psycopg2-binary python-dotenv Pillow
```
- Optional dev tools: `drf-spectacular`, `coverage`, `black`, `isort`.
- Create `.env` with secrets placeholders (to be filled later): `SECRET_KEY`, `DATABASE_URL`, `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`, `AUTO_APPROVE_COMMENTS`, `ALLOWED_HOSTS`.

### Step 2: Configure Django Settings
- In `core/settings.py`:
  - Add apps: `rest_framework`, `corsheaders`, `django_filters`, `accounts`, `payments`, `processing`, `bots`, `demo`, `blog`.
  - Set `AUTH_USER_MODEL = "accounts.Student"`.
  - Configure `REST_FRAMEWORK` (pagination, authentication, permissions, filtering, versioning).
  - Enable `CORS_ALLOWED_ORIGINS` or `CORS_ALLOW_ALL_ORIGINS` (dev only).
  - Set `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`; set `MEDIA_URL`, `MEDIA_ROOT`.
  - Configure database (Postgres via `DATABASE_URL` in prod; SQLite for local if desired).
  - Add `TEMPLATES` dirs for site templates (e.g., `templates/`).

### Step 3: URLs Baseline (API + Site)
- In `core/urls.py`:
  - Include per‑app API routers under `/api/...`.
  - Add Django admin at `/admin/`.
  - Add site pages routes (home, blog list/detail) served via templates.

### Step 4: Accounts App — Model
- Create `Student` model extending `AbstractUser` with fields: `phone` (CharField), optional `avatar`, and any profile fields required.
- Set `USERNAME_FIELD`/`REQUIRED_FIELDS` as needed.

### Step 5: Accounts App — Serializers & API
- Add serializers: `StudentSerializer`, `RegisterSerializer`, `ProfileSerializer`.
- Views:
  - `POST /api/users/` to register new users.
  - `GET/PUT/PATCH/DELETE /api/users/{id}/` for profile CRUD (owner or admin).
- Configure token/session auth (DRF TokenAuth or JWT if preferred). Expose login endpoints.

### Step 6: Payments App — Models
- Create `BotInstance` model: fields `owner(FK Student)`, `reference(UUID/slug)`, `note_count`, `status(choices: pending|processing|ready|failed)`, `bot_url`, timestamps.
- Create `PaymentTransaction` model: `reference`, `amount`, `currency`, `status`, `raw_payload(JSON)`, `student(FK)`.
- Add indexes on `reference`, `status`.

### Step 7: Payments App — API (Paystack)
- Endpoints:
  - `POST /api/payments/init/` → initialize transaction with Paystack (NGN/USD), return authorization URL and reference; create `PaymentTransaction(pending)`.
  - `POST /api/payments/webhook/` → verify signature, confirm event, update `PaymentTransaction`, and on success create `BotInstance(status=pending)`.
- Add Paystack service module for init/verify logic; use env keys.

### Step 8: Processing App — Admin‑Only Interface
- Provide admin UI to attach uploaded notes (images/PDF) to a `BotInstance` and mark OCR cleanup complete.
- Add models if needed (e.g., `NoteAsset` linked to `BotInstance`).
- Implement a management command or admin action to seed vetted Q&A pairs to the `bots` app from cleaned notes.

### Step 9: Bots App — Models
- `Question`: `bot(FK BotInstance)`, `text`.
- `Answer`: `question(OneToOne)`, `text`.
- `Review`: `bot(FK)`, `student(FK)`, `rating(Int 1..5)`, `comment`, `created_at`.
- Index `bot`, `created_at`.

### Step 10: Bots App — API (Q&A + Reviews)
- Endpoints:
  - `GET /api/bots/{reference}/questions/` → returns vetted question list for the bot (or demo bot).
  - `POST /api/bots/{reference}/answer/` → body `{ "question_id" | "text" }`; returns matching answer or `status` if bot not ready.
  - `GET /api/reviews/?bot={bot_id}` → list reviews.
  - `POST /api/reviews/` → create review (authenticate; owner must have bot).
  - `PUT/PATCH/DELETE /api/reviews/{id}/` → owner or admin only.
- Permissions: safe methods public where appropriate; writes require auth; object‑level checks.

### Step 11: Demo App — Seed Data & Public Demo
- Create a demo `BotInstance` with a fixed reference and several Q&A pairs.
- Expose the same Q&A endpoints using the demo reference.
- Add templates or footer partial to embed a Botpress demo bot.

### Step 12: Blog App — Models
- `Category`: `name`, `slug` (unique).
- `Tag`: `name`, `slug` (unique).
- `Post`: `title`, `slug`, `author(FK Student)`, `content`, `excerpt`, `cover_image`, `status(draft|published|archived)`, `published_at`, M2M `categories`, M2M `tags`, timestamps.
- `Comment`: `post(FK)`, `author(FK Student, nullable if anonymous allowed)`, `parent(FK Comment, null)`, `content`, `status(pending|approved|rejected)`, timestamps.
- Add indexes on `slug`, `published_at`, `status`.

### Step 13: Blog App — Serializers
- `CategorySerializer`, `TagSerializer`.
- `PostSerializer` (list), `PostDetailSerializer` (detail; include rendered markdown/HTML if used), nested categories/tags.
- `CommentSerializer` (with `parent` id support).

### Step 14: Blog App — API (Routers & Views)
- Posts:
  - `GET /api/blog/posts/` (search by `q`, filter by `author`, `category`, `tag`; paginate).
  - `POST /api/blog/posts/` (author/admin).
  - `GET /api/blog/posts/{id or slug}/`.
  - `PUT/PATCH/DELETE /api/blog/posts/{id or slug}/` (author/admin).
- Comments:
  - `GET /api/blog/posts/{post_id}/comments/?status=approved`.
  - `POST /api/blog/posts/{post_id}/comments/` (authenticated; `{ content, parent? }`).
  - `PUT/PATCH/DELETE /api/blog/comments/{id}/` (owner or moderator).
  - `POST /api/blog/comments/{id}/moderate/` (approve/reject; admin/moderator only).
- Categories/Tags: `GET` list; `POST` admin; `PUT/PATCH/DELETE` admin.
- Enable `django-filter` and `SearchFilter` for `q` over `title`, `content`, `tags__name`.

### Step 15: Global Search Endpoint (Optional but Recommended)
- `GET /api/search/?q=keyword&type=posts|bots|reviews` → aggregate results from blog posts, bot questions, and reviews.
- Implement thin orchestrator view that queries each app with filters and returns a unified payload.

### Step 16: Permissions, Auth, Pagination, Throttling
- Default permission: read‑only for public endpoints; authenticated for writes.
- Object‑level permissions for: post ownership, comment ownership, review ownership.
- Pagination defaults (e.g., page size 10).
- Throttling for comment creation to mitigate spam.

### Step 17: Admin Registration & Moderation Tools
- Register `Post`, `Category`, `Tag`, `Comment`, `BotInstance`, `Question`, `Answer`, `Review`, `PaymentTransaction`, and any processing models.
- Admin list filters and search: `status`, `author`, `published_at`.
- Admin actions: approve/reject comments, bulk archive posts, mark bot as ready, reseed Q&A from notes.

### Step 18: Templates (Site Pages)
- Create `templates/` with:
  - `base.html` (site shell, nav/footer with recent posts widget and demo bot embed link).
  - `home.html` (marketing copy; CTA to upload/checkout; demo link).
  - `blog/list.html` and `blog/detail.html` (consume API via server‑side render or HTMX/fetch).
  - `bots/status.html` (optional: show bot status and link to bot URL).
- Use template context or small JS fetches to call API endpoints.

### Step 19: Static Files
- Create `static/` for CSS/JS/images. Use a basic stylesheet and a minimal JS bundle to handle API calls (comments submit, search, etc.).
- Configure `collectstatic`; in production, serve via Whitenoise or a CDN.

### Step 20: Botpress Integration
- Store `bot_url` in `BotInstance` after processing.
- Add Botpress embed snippet on an internal page (e.g., demo page) conditionally.
- Optionally link a post to a `BotInstance` for contextual embeds.

### Step 21: Tests (Unit, API, Integration)
- Models: slug generation, status transitions, constraints.
- Serializers: validation rules for posts/comments/reviews.
- Views/API: posts CRUD, comments lifecycle (pending → approved), payments init & webhook, bots Q&A, reviews CRUD, search endpoint.
- Use DRF test client; add fixtures for demo data.

### Step 22: Seed Demo Data
- Management command to create: one demo `BotInstance` with Q&A pairs; 5 blog posts with categories/tags; a handful of approved/pending comments; 2 reviews.
- Run command locally and in staging.

### Step 23: Deployment (Heroku or PythonAnywhere)
- Add `gunicorn`, `whitenoise`, `django-storages[boto3]` to requirements.
- Create `Procfile` (`web: gunicorn core.wsgi`).
- Configure environment vars: `SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, `PAYSTACK_*`, `AWS_*`, `AUTO_APPROVE_COMMENTS`, `DEBUG=0`.
- Static & media:
  - Local: Whitenoise for static; local `MEDIA_ROOT`.
  - Prod: S3 for media (and optionally static). Ensure `collectstatic` on release.
- Run `makemigrations`/`migrate` on deploy.
- Set Paystack webhook URL to `/api/payments/webhook/` on live domain.

### Step 24: Caching & Performance
- Enable Redis cache for recent posts and comment counts.
- Cache `GET /api/blog/posts/` list and `recent posts` footer widget.
- Add ETag/Last‑Modified headers where easy.

### Step 25: Monitoring & Logging
- Configure request logging for API and webhook events.
- Add error monitoring (Sentry) and health check endpoint.

### Step 26: Security Hardening
- Enforce HTTPS, secure cookies, CSRF on non‑API forms, and webhook signature verification.
- Rate‑limit comment creation and login attempts.
- Validate file uploads (content‑type and size) for notes and images.

### Step 27: API Documentation
- Add `drf-spectacular` to generate OpenAPI schema at `/api/schema/` and interactive docs at `/api/docs/` and `/api/redoc/`.
- Annotate views/serializers for rich schema.

### Step 30: Developer Tooling (Black, isort, Coverage)
- Add `pyproject.toml` with Black and isort settings (compatible profiles).
- Add `.coveragerc` to measure API and app coverage; omit migrations and settings.
- Add `coverage` commands to README: `coverage run -m pytest` and `coverage html`.

### Step 28: Final QA & E2E
- Run full test suite and coverage.
- Manual E2E: user registers → pays → webhook creates bot → admin processes notes/Q&A → bot ready → student queries via API and Botpress link → leaves review → blog browsing and comments with moderation → global search.

### Step 29: Release & Handover
- Freeze requirements, export environment configuration, backup DB, and write final runbook.
- Prepare onboarding docs for moderators (comment approvals) and operators (processing flow).

---

#### Deliverables by Phase
- API: All endpoints under `/api/...` functioning and documented.
- Site: Templates and static assets live; demo bot embedded; recent posts widget.
- Admin: Full moderation and processing workflows.
- Tests: Green CI.
- Deployment: Production on Heroku/PythonAnywhere with S3 and Redis where applicable.

#### Notes
- All blog interactions use Django ORM only.
- Reviews enforce ownership; comments default to pending unless `AUTO_APPROVE_COMMENTS=True` (MVP/testing only).
- Use UUIDs for references to keep URLs opaque.
