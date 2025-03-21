import pathlib
from importlib import import_module

dir = pathlib.Path(__file__).parent

# Import all modules in the agents directory
for file in dir.rglob("**/*.py"):
    if "__init__" in file.name:
        continue
    import_module(f".{file.stem}", __name__)
