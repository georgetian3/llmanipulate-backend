# LLManipulate Backend

## Dependencies

All requirements are stored in `requirements/`. 
- `base.txt`: dependencies that are used in both local and prod environments, e.g. `fastapi`
- `local.txt`: dependencies that are used in local only, e.g. `pytest`
- `prod.txt`: depencendies that are used in prod only, e.g. `uvicorn`

## Development

1. Install dependencies, preferably in a virtual environment: `pip install -r requirements/local.txt`
2. Run development server: `fastapi dev apis`

Default settings uses a local SQLite database and stateless JWT authentication backend which does not require access to Redis.

## Design Principles

- `apis/` should only handle API specification, requests/responses, parameters etc. Contains minimal business logic which should be delegated to code within `services/`
- `models/` should only only be used to define database models and database interfacing
- `services/` should contain all other functionalities, the majority of which being business logic

## Linting, formatting, typechecking

Use [Ruff](https://docs.astral.sh/ruff/)