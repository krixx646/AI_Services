### API Endpoints — Postman Step-by-Step

This guide shows how to test all major endpoints with Postman. Protected endpoints use JWT Bearer tokens from the login response.

## 0) Prerequisites
- Base URL (local): `http://127.0.0.1:8000`
- A test user account (or create via Register)

## 1) Create a Postman Environment
Create an environment (e.g., "AI_Services Local") with variables:
- `base_url` = `http://127.0.0.1:8000`
- `email` = your test email (e.g., `you@example.com`)
- `password` = your test password (e.g., `yourpass123`)
- `access` = leave empty (will be set after login)

You can reference variables in requests as `{{base_url}}`, `{{email}}`, etc.

## 2) Accounts

### 2.1 Register (Public)
- Method: POST
- URL: `{{base_url}}/api/accounts/register/`
- Body (JSON):
{
  "email": "{{email}}",
  "password": "{{password}}",
  "confirm_password": "{{password}}",
  "username": "tester"
}
- Expect: 201 Created, `{ "message": "Registration successful" }`

### 2.2 Login (Public → returns JWT)
- Method: POST
- URL: `{{base_url}}/api/accounts/login/`
- Body (JSON):
{
  "email": "{{email}}",
  "password": "{{password}}"
}
- Scripts → Tests sub-tab (save token to env):
const data = pm.response.json();
pm.environment.set('access', data.access);
- After this, set Authorization on the collection (or the protected requests):
  - Type: Bearer Token
  - Token: `{{access}}`

### 2.3 Profile (Protected)
- List (GET): `{{base_url}}/api/accounts/profile/`
- Detail (GET): `{{base_url}}/api/accounts/profile/<id>/`
- Update (PATCH): `{{base_url}}/api/accounts/profile/<id>/`
  - Body: `{ "bio": "Hello world" }`
- Requires Bearer token.

## 3) Blog (Public for GET; writes may require auth/perms)

### 3.1 Posts
- List (GET): `{{base_url}}/api/blog/posts/`
- Retrieve (GET): `{{base_url}}/api/blog/posts/<id>/`

### 3.2 Categories
- List (GET): `{{base_url}}/api/blog/categories/`
- Retrieve (GET): `{{base_url}}/api/blog/categories/<id>/`

### 3.3 Tags
- List (GET): `{{base_url}}/api/blog/tags/`
- Retrieve (GET): `{{base_url}}/api/blog/tags/<id>/`

### 3.4 Comments
- Under a post (GET/POST): `{{base_url}}/api/blog/posts/<post_id>/comments/`
- Moderate (PUT/PATCH): `{{base_url}}/api/blog/comments/<comment_id>/moderate/`
- Detail (GET/DELETE): `{{base_url}}/api/blog/comments/<comment_id>/`

## 4) Bots

### 4.1 Reviews (GET public, POST protected)
- List (GET): `{{base_url}}/api/bots/reviews/`
- Create (POST): `{{base_url}}/api/bots/reviews/`
  - Body (JSON): `{ "bot": <bot_id>, "rating": 5, "comment": "Great" }`

### 4.2 Questions / Answer (by bot reference)
- Questions (GET): `{{base_url}}/api/bots/<reference>/questions/`
- Answer (POST): `{{base_url}}/api/bots/<reference>/answer/`
  - Body (JSON): `{ "question": "What is this bot about?" }`

## 5) Payments (Protected)

### 5.1 Initialize
- POST `{{base_url}}/api/payments/init/`
- Body (JSON):
{
  "amount": 9000,
  "currency": "NGN",
  "plan": "starter",
  "express": false
}
- Expect JSON with `authorization_url` to redirect user to Paystack.

### 5.2 Verify
- GET `{{base_url}}/api/payments/verify/<reference>/`
- Returns Paystack verification result; backend also updates stored status.

### 5.3 Webhook (Paystack → Your API)
- POST `{{base_url}}/api/payments/webhook/`
- Configured on Paystack dashboard; not typically called from Postman.

### 5.4 Success Page (HTML)
- GET `{{base_url}}/api/payments/success/?reference=<reference>`

## 6) Demo (Public)
- GET `{{base_url}}/api/demo/info/`

## 7) Global Search (Public)
- GET `{{base_url}}/api/search/?q=keyword&type=all`
- `type` can be `all`, `posts`, `bots`, `reviews`.

---

## Recommended Postman Collection Structure
- Accounts
  - Register (POST)
  - Login (POST) [Tests saves `access`]
  - Profile List (GET)
  - Profile Detail (GET/PATCH)
- Blog
  - Posts (GET/GET id)
  - Categories (GET)
  - Tags (GET)
  - Comments (post routes)
- Bots
  - Reviews (GET/POST)
  - Questions (GET by reference)
  - Answer (POST)
- Payments
  - Init (POST)
  - Verify (GET)
- Demo
  - Info (GET)
- Search
  - Search (GET)

Set collection Authorization to Bearer Token with `{{access}}` so protected requests inherit it. Run in order: Register → Login → others.

## Troubleshooting
- 401/403: Ensure Authorization is Bearer `{{access}}` and token is fresh.
- 400 on payments init: Check numeric `amount` and allowed `currency` (NGN by default).
- USD toggle: Only shows if enabled in server settings.
