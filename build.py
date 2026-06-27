import json
import pathlib

from src import structs
from src.agents import AGENTS, LOCAL_MODEL
from src.consts import DEVELOPER_BASH, Approval

DEFAULT_MODEL = LOCAL_MODEL
OPENCODE_FILE = pathlib.Path("./opencode/opencode.json")
AGENTS_DIR = pathlib.Path("./opencode/agents/")


def main() -> None:
    open_code = structs.OpenCode(
        model=DEFAULT_MODEL,
        permission=structs.Permissions.make(
            bash=DEVELOPER_BASH,
            task={},
            default_approval=Approval.ALLOW,
            edit_approval=Approval.ALLOW,
            webfetch_approval=Approval.ALLOW,
        ),
        agent={agent.name: agent for agent in AGENTS},
    )
    data = open_code.build()
    OPENCODE_FILE.write_text(json.dumps(data, indent=2))

    for agent in AGENTS:
        out_file = AGENTS_DIR / (agent.name + ".md")
        agent.make_agent_md(out_file)


if __name__ == "__main__":
    main()
