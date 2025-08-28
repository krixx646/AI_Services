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
SECRET_KEY=change-me
PAYSTACK_PUBLIC_KEY=pk_live_xxx
PAYSTACK_SECRET_KEY=sk_live_xxx
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
