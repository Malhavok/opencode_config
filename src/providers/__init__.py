from src.providers.provider import ExternalProvider, Provider

from .ollama import Ollama
from .opencode_zen import OpenCodeZen

OLLAMA = Ollama()
OPEN_CODE_ZEN = OpenCodeZen()

EXTERNAL_PROVIDERS: dict[str, ExternalProvider] = {
    OLLAMA.get_tag(): OLLAMA,
}

RAW_PROVIDERS: dict[str, Provider] = {
    OPEN_CODE_ZEN.get_tag(): OPEN_CODE_ZEN,
}

ALL_PROVIDERS: dict[str, Provider] = {
    **EXTERNAL_PROVIDERS,
    **RAW_PROVIDERS,
}
