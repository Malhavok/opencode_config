class Provider:
    def get_tag(self) -> str:
        raise NotADirectoryError()

    def get_name(self) -> str:
        raise NotADirectoryError()

    def get_npm(self) -> str:
        raise NotADirectoryError()

    def get_options(self) -> dict[str, str]:
        raise NotADirectoryError()

    def get_models(self) -> list[str]:
        raise NotImplementedError()

    def get_models_with_names(self) -> dict[str, str]:
        # Maps printable-name –> actual name of the model.
        raise NotADirectoryError()

    def get_provider_config(self) -> dict[str, dict[str, str | dict]]:
        return {
            self.get_tag(): {
                "name": self.get_name(),
                "npm": self.get_npm(),
                "options": self.get_options(),
                "models": {
                    model_name: {"name": printable_name}
                    for printable_name, model_name in self.get_models_with_names().items()
                },
            }
        }
