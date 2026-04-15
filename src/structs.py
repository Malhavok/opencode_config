import dataclasses
import enum
import pathlib
from typing import Any, Self

from .consts import SAFE_BASH, Approval


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

        return base_dict
