import enum


class Approval(enum.StrEnum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


SAFE_BASH = {
    elem: Approval.ALLOW
    for elem in [
        "git status*",
        "git diff*",
        "grep *",
        "rg *",
        "find *",
        "ls *",
        "pwd",
        "head *",
        "tail *",
        "diff *",
        "cat *",
        "wc *",
        "echo *",
    ]
}

DEVELOPER_BASH = dict(
    **{
        elem: Approval.ALLOW
        for elem in [
            "mkdir *",
            "npm test*",
            "pnpm test*",
            "pytest*",
            "go test*",
            "cargo test*",
            "mix *",
            "docker compose *",
        ]
    },
    **SAFE_BASH,
)
