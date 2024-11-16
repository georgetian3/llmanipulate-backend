# LLManipulate

## Dependencies

All requirements are stored in `requirements/`. 
- `base.txt`: dependencies that are used in both local and prod environments, e.g. `fastapi`
- `local.txt`: dependencies that are used in local only, e.g. `pytest`
- `prod.txt`: depencendies that are used in prod only, e.g. `uvicorn`

## Development

1. Install dependencies: `pip install -r requirements/local.txt`
2. Ensure all environment variables referred to in `config.py` are defined in `.env`. A minimal `.env` using a local SQLite3 database is:

```
DATABASE_DATABASE=llmanipulate.sqlite3
DATABASE_DRIVERNAME='sqlite+aiosqlite'
```

3. Run development server: `fastapi dev main.py`

## Design Principles

- `apis/` should only handle API specification, requests/responses, parameters etc. Contains minimal business logic which should be delegated to code within `services/`
- `models/` should only only be used to define database models and database interfacing
- `services/` should contain all other functionalities, the majority of which being business logic

## Linting, formatting, typechecking

```
black .
flake8 .
isort .
mypy .
```