import subprocess

from .provider import Provider


class Ollama(Provider):
    LS_TIMEOUT_SECONDS = 10
    PROMPT_TIMEOUT_SECONDS = 60

    def __init__(self):
        self._models = None
        self._model_names = {}

    def get_tag(self) -> str:
        return "ollama"

    def get_name(self) -> str:
        return "Ollama (local)"

    def get_npm(self) -> str:
        return "@ai-sdk/openai-compatible"

    def get_options(self) -> dict[str, str]:
        return {
            "baseURL": "http://localhost:11434/v1",
        }

    def get_models(self) -> list[str]:
        if self._models is not None:
            return self._models

        result = subprocess.run(
            ["ollama", "ls"],
            stdout=subprocess.PIPE,
            timeout=self.LS_TIMEOUT_SECONDS,
            text=True,
        )
        assert result.returncode == 0
        self._models = [line.split()[0] for line in result.stdout.splitlines()[1:]]
        return self._models

    def get_models_with_names(self) -> dict[str, str]:
        return {
            self._get_model_printable_name(model): model for model in self.get_models()
        }

    def _get_model_printable_name(self, model_name: str) -> str:
        if model_name in self._model_names:
            return self._model_names[model_name]

        result = subprocess.run(
            [
                "ollama",
                "run",
                model_name,
                "--keepalive",
                "0m",
                "--hidethinking",
                "Print just your model name",
            ],
            stdout=subprocess.PIPE,
            timeout=self.PROMPT_TIMEOUT_SECONDS,
            text=True,
        )
        assert result.returncode == 0

        lines = [
            stripped
            for line in result.stdout.splitlines()
            if len(stripped := line.strip()) > 0
        ]
        return lines[-1]


if __name__ == "__main__":
    ollama = Ollama()
    print(ollama.get_models_with_names())
