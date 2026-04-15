import json
import pathlib
import shutil

from src import structs
from src.agents import AGENTS
from src.consts import SAFE_BASH, Approval

DEFAULT_MODEL = "opencode/claude-opus-4-6"
OPENCODE_FILE = pathlib.Path("./opencode/opencode.json")
AGENTS_DIR = pathlib.Path("./opencode/agents/")


def main() -> None:
    open_code = structs.OpenCode(
        model=DEFAULT_MODEL,
        permission=structs.Permissions.make(
            bash=SAFE_BASH, task={}, default_approval=Approval.ASK
        ),
        agent={agent.name: agent for agent in AGENTS},
    )
    data = open_code.build()
    OPENCODE_FILE.write_text(json.dumps(data, indent=2))

    for agent in AGENTS:
        out_file = AGENTS_DIR / (agent.name + ".md")
        shutil.copyfile(agent.template, out_file)


if __name__ == "__main__":
    main()
