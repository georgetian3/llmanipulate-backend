# [pending project name]

# Dependencies

All requirements are stored in `requirements/`. 
- `base.txt`: dependencies that are used in both local and prod environments, e.g. `fastapi`
- `local.txt`: dependencies that are used in local only, e.g. `pytest`
- `prod.txt`: depencendies that are used in produ only, e.g. `uvicorn`

# Development

1. Install dependencies: `pip install -r requirements/local.txt`
2. Ensure all environment variables referred to in `config.py` are defined in `.env`. A minimal `.env` is:
```

```
3. Run development server: `fastapi dev main.py`



# Linting, formatting, typechecking

```
black .
flake8 .
isort .
mypy .
```