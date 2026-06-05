import re
from typing import Any


class Provider:
    def __init__(self):
        self._models = None
        self._model_names = None

    def has_model(self, model_name: str) -> bool:
        return model_name in self.get_models()

    def get_models(self) -> list[str]:
        if self._models is None:
            self._models = self._get_models()
        return self._models

    def get_models_with_names(self) -> dict[str, str]:
        return {
            self._get_model_printable_name(model): model for model in self.get_models()
        }

    def _get_model_printable_name(self, model_name: str) -> str:
        base_name = model_name.split(":", maxsplit=1)[0]

        match = re.search(r"([^\d]*)(.*)", base_name)
        if match is None:
            return base_name

        name = match.group(1).capitalize()
        version = match.group(2)
        return f"{name} {version}"

    def _get_models(self) -> list[str]:
        raise NotImplementedError()


class ExternalProvider(Provider):
    def __init__(self):
        self._models = None
        self._model_names = None

    def get_tag(self) -> str:
        raise NotADirectoryError()

    def get_name(self) -> str:
        raise NotADirectoryError()

    def get_npm(self) -> str:
        raise NotADirectoryError()

    def get_options(self) -> dict[str, str]:
        raise NotADirectoryError()

    def get_provider_config(self) -> dict[str, Any]:
        return {
            "name": self.get_name(),
            "npm": self.get_npm(),
            "options": self.get_options(),
            "models": {
                model_name: {"name": printable_name}
                for printable_name, model_name in self.get_models_with_names().items()
            },
        }
