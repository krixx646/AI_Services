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
