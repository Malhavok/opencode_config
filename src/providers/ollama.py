import subprocess

from .provider import ExternalProvider


class Ollama(ExternalProvider):
    LS_TIMEOUT_SECONDS = 10
    PROMPT_TIMEOUT_SECONDS = 120

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

    def _get_models(self) -> list[str]:
        result = subprocess.run(
            ["ollama", "ls"],
            stdout=subprocess.PIPE,
            timeout=self.LS_TIMEOUT_SECONDS,
            text=True,
        )
        assert result.returncode == 0
        return [line.split()[0] for line in result.stdout.splitlines()[1:]]


if __name__ == "__main__":
    ollama = Ollama()
    print(ollama.get_models_with_names())
