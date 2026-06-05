from .ollama import Ollama

OLLAMA = Ollama()

EXTERNAL_PROVIDERS = {
    OLLAMA.get_tag(): OLLAMA,
}

ALL_PROVIDERS = EXTERNAL_PROVIDERS
