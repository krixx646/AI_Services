import os
import time
import json
import requests


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
EMAIL = os.getenv("TEST_EMAIL") or f"testuser_{int(time.time())}@example.com"
PASSWORD = os.getenv("TEST_PASSWORD", "yourpass123")
DO_PAYMENTS = os.getenv("DO_PAYMENTS", "false").lower() == "true"


session = requests.Session()
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})


def abs_url(path: str) -> str:
    return f"{BASE_URL.rstrip('/')}{path}"


def print_resp(title: str, resp: requests.Response) -> None:
    try:
        body = resp.json()
    except Exception:
        body = resp.text
    print(f"\n== {title} [{resp.status_code}] ==")
    if isinstance(body, str):
        print(body[:2000])
    else:
        print(json.dumps(body, indent=2)[:2000])


def ensure_register(email: str, password: str) -> None:
    payload = {
        "email": email,
        "password": password,
        "confirm_password": password,
        "username": email.split("@")[0],
    }
    r = session.post(abs_url("/api/accounts/register/"), data=json.dumps(payload), timeout=15)
    print_resp("Register (ok if already exists)", r)


def login(email: str, password: str) -> None:
    r = session.post(
        abs_url("/api/accounts/login/"), data=json.dumps({"email": email, "password": password}), timeout=15
    )
    print_resp("Login", r)
    r.raise_for_status()
    token = (r.json() or {}).get("access")
    if not token:
        raise RuntimeError("Login succeeded but no access token returned")
    session.headers["Authorization"] = f"Bearer {token}"


def profile_checks() -> None:
    r = session.get(abs_url("/api/accounts/profile/"), timeout=15)
    print_resp("Profile list", r)


def blog_public() -> None:
    print_resp("Blog posts", session.get(abs_url("/api/blog/posts/"), timeout=15))
    print_resp("Blog categories", session.get(abs_url("/api/blog/categories/"), timeout=15))
    print_resp("Blog tags", session.get(abs_url("/api/blog/tags/"), timeout=15))


def global_search() -> None:
    print_resp("Search all", session.get(abs_url("/api/search/?q=chat&type=all"), timeout=15))


def demo_and_bot() -> None:
    r = session.get(abs_url("/api/demo/info/"), timeout=15)
    print_resp("Demo info", r)
    if not r.ok:
        return
    ref = (r.json() or {}).get("reference")
    if not ref:
        return
    print_resp("Bot questions", session.get(abs_url(f"/api/bots/{ref}/questions/"), timeout=15))
    ans_payload = {"question": "What is this bot about?"}
    print_resp(
        "Bot answer",
        session.post(abs_url(f"/api/bots/{ref}/answer/"), data=json.dumps(ans_payload), timeout=20),
    )


def reviews_list() -> None:
    print_resp("Reviews list", session.get(abs_url("/api/bots/reviews/"), timeout=15))


def payments_init() -> None:
    if not DO_PAYMENTS:
        print("\n== Payments skipped (set DO_PAYMENTS=true to run) ==")
        return
    payload = {"amount": 9000, "currency": "NGN", "plan": "starter", "express": False}
    r = session.post(abs_url("/api/payments/init/"), data=json.dumps(payload), timeout=20)
    print_resp("Payments init", r)


def main() -> None:
    print(f"Base URL: {BASE_URL}")
    print(f"Email: {EMAIL}")
    ensure_register(EMAIL, PASSWORD)
    login(EMAIL, PASSWORD)
    profile_checks()
    blog_public()
    global_search()
    demo_and_bot()
    reviews_list()
    payments_init()
    print("\nDone.")


if __name__ == "__main__":
    main()


