import enum
import pathlib

from .consts import DEVELOPER_BASH, SAFE_BASH, Approval
from .structs import Agent, Mode, Permissions

DEFAULT_TASK = {
    "*": Approval.DENY,
}


ARCHITECT_TEMPLATE = pathlib.Path("./templates/architect.md")
DEVELOPER_TEMPLATE = pathlib.Path("./templates/developer.md")
REVIEWER_STRICT_DIFF_TEMPLATE = pathlib.Path("./templates/reviewer-strict-diff.md")
REVIEWER_ALTERNATIVE_TEMPLATE = pathlib.Path(
    "./templates/reviewer-alternative-perspective.md"
)
REVIEWER_SENIOR_TEMPLATE = pathlib.Path("./templates/reviewer-senior.md")

CAVEMAN_TEMPLATE = pathlib.Path("./templates/caveman.md")


class ReviewerTemplate(enum.Enum):
    STRICT_DIFF = REVIEWER_STRICT_DIFF_TEMPLATE
    ALTERNATIVE = REVIEWER_ALTERNATIVE_TEMPLATE
    SENIOR = REVIEWER_SENIOR_TEMPLATE


def make_architect(
    name: str,
    model: str,
    developers: list[str],
    reviewers: list[str],
    additional_rules: list[pathlib.Path] | None = None,
) -> Agent:
    return Agent(
        name=name,
        mode=Mode.PRIMARY,
        description="Plans features and bugfixes, writes plan files, and orchestrates developer and reviewers.",
        model=model,
        permission=Permissions(
            edit=Approval.ALLOW,
            webfetch=Approval.ASK,
            bash=SAFE_BASH,
            task=dict(
                **DEFAULT_TASK,
                **{dev: Approval.ALLOW for dev in developers},
                **{rev: Approval.ALLOW for rev in reviewers},
            ),
        ),
        template=ARCHITECT_TEMPLATE,
        additional_rules=additional_rules,
    )


def make_developer(
    name: str,
    model: str,
    reviewers: list[str],
    additional_rules: list[pathlib.Path] | None = None,
) -> Agent:
    return Agent(
        name=name,
        mode=Mode.SUBAGENT,
        description="Implements only the approved plan, then asks reviewers to review the diff.",
        model=model,
        permission=Permissions(
            edit=Approval.ALLOW,
            webfetch=Approval.ASK,
            bash=DEVELOPER_BASH,
            task=dict(
                **DEFAULT_TASK,
                **{rev: Approval.ALLOW for rev in reviewers},
            ),
        ),
        template=DEVELOPER_TEMPLATE,
        additional_rules=additional_rules,
    )


def make_reviewer(
    name: str,
    model: str,
    behaviour_template: ReviewerTemplate,
    additional_rules: list[pathlib.Path] | None = None,
) -> Agent:
    return Agent(
        name=name,
        mode=Mode.SUBAGENT,
        description="Reviewer with given template.",
        model=model,
        permission=Permissions(
            edit=Approval.DENY,
            webfetch=Approval.DENY,
            bash=SAFE_BASH,
            task=DEFAULT_TASK,
        ),
        template=behaviour_template.value,
        additional_rules=additional_rules,
    )
