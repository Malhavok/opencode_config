import dataclasses
import enum
import pathlib
import string
from typing import Any, Self

from src.providers import ALL_PROVIDERS, EXTERNAL_PROVIDERS

from .consts import PRICE_PREFIX_ORDER, Approval, Variants


class Mode(enum.StrEnum):
    PRIMARY = "primary"
    SUBAGENT = "subagent"


@dataclasses.dataclass
class Permissions:
    edit: Approval
    webfetch: Approval
    bash: dict[str, Approval]
    task: dict[str, Approval]

    @classmethod
    def make(
        cls,
        bash: dict[str, Approval],
        task: dict[str, Approval],
        default_approval: Approval = Approval.ASK,
        edit_approval: Approval = Approval.ASK,
        webfetch_approval: Approval = Approval.ASK,
    ) -> Self:
        return cls(
            edit=edit_approval,
            webfetch=webfetch_approval,
            bash=dict(
                **bash,
                **{"*": default_approval},
            ),
            task=dict(
                **task,
                **{"*": default_approval},
            ),
        )


@dataclasses.dataclass
class Agent:
    name: str
    mode: Mode
    description: str
    model: str
    variant: Variants
    permission: Permissions
    template: pathlib.Path
    additional_rules: list[pathlib.Path] | None

    def make_agent_md(self, out_path: pathlib.Path) -> None:
        rules_content = []
        for additional_rule_file in self.additional_rules or []:
            rules_lines = additional_rule_file.read_text().splitlines()
            rules_content.extend(rules_lines)

        template_obj = string.Template(self.template.read_text())
        content = template_obj.substitute(
            {
                "POST_RULES": "\n".join(rules_content),
                "SORTED_EXPENSES_PREFIXES": ", ".join(PRICE_PREFIX_ORDER),
            }
        )
        out_path.write_text(content)


@dataclasses.dataclass
class OpenCode:
    model: str
    permission: Permissions
    agent: dict[str, Agent]

    def build(self) -> dict[str, Any]:
        base_dict = dataclasses.asdict(self)
        base_dict["$schema"] = "https://opencode.ai/config.json"

        # Silly install for context-mode. This should be done better in the future.
        base_dict["mcp"] = {
            "context-mode": {"type": "local", "command": ["context-mode"]},
            "serena": {
                "type": "local",
                "command": ["serena", "start-mcp-server", "--context=ide"],
            },
        }
        base_dict["plugin"] = [
            "context-mode",
            "./submodules/ponytail/.opencode/plugins/ponytail.mjs",
        ]
        base_dict["provider"] = {}

        for provider_tag, provider in EXTERNAL_PROVIDERS.items():
            base_dict["provider"][provider_tag] = provider.get_provider_config()

        for agent_dict in base_dict["agent"].values():
            del agent_dict["name"]
            del agent_dict["template"]
            del agent_dict["additional_rules"]

        self._validate_agents(base_dict["agent"])
        return base_dict

    def _validate_agents(self, agents_dict: dict[str, Any]) -> None:
        missing_models = {}

        for agent_name, config in agents_dict.items():
            provider_name, model = config["model"].split("/", maxsplit=1)
            if provider_name not in ALL_PROVIDERS:
                print(
                    f"Unable to check model for agent {agent_name} – {provider_name} not available."
                )
                continue

            provider = ALL_PROVIDERS[provider_name]
            if not provider.has_model(model):
                missing_models[agent_name] = model
                print(
                    f"Model {model} from provider {provider_name} for agent {agent_name} is not available."
                )

        if len(missing_models) > 0:
            raise ValueError(f"Missing models: {missing_models}.")
