import json

from fastapi.openapi.utils import get_openapi


class Api:
    def __init__(self): ...

    def write_openapi(self):
        with open("openapi.json", "w") as f:
            json.dump(
                get_openapi(
                    title=self.api.title,
                    version=self.api.version,
                    openapi_version=self.api.openapi_version,
                    description=self.api.description,
                    routes=self.api.routes,
                ),
                f,
                indent=4,
                ensure_ascii=False,
            )
