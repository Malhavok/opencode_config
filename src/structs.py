import dataclasses
import enum
import pathlib
import string
from typing import Any, Self

from .consts import PRICE_PREFIX_ORDER, Approval


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
    ) -> Self:
        return cls(
            edit=Approval.ASK,
            webfetch=Approval.ASK,
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
    permission: Permissions
    template: pathlib.Path
    additional_rules: list[pathlib.Path] | None = None

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

        for agent_dict in base_dict["agent"].values():
            del agent_dict["name"]
            del agent_dict["template"]
            del agent_dict["additional_rules"]

        return base_dict
