import enum

PRO_PREFIX = "pro-"
MEDIUM_PREFIX = "medium-"
CHEAP_PREFIX = "cheap-"
FREE_PREFIX = "free-"

PRICE_PREFIX_ORDER = [FREE_PREFIX, CHEAP_PREFIX, MEDIUM_PREFIX, PRO_PREFIX]


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
