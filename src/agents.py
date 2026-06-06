from .consts import CHEAP_PREFIX, LOCAL_PREFIX, PRO_PREFIX
from .roles import (
    ADD_PLAN_REVIEWER_TEMPLATE,
    ReviewerTemplate,
    make_architect,
    make_developer,
    make_reviewer,
)

ARCHITECT_NAME = "architect"
DEVELOPER_NAME = "developer"
STRICT_REVIEWER_NAME = "reviewer-strict-diff"
ALTERNATIVE_REVIEWER_NAME = "reviewer-alternative"
SENIOR_REVIEWER_NAME = "reviewer-senior"
ARCHITECT_REVIEWER_NAME = "architect-reviewer"

REVIEWERS_NAMES = [
    ALTERNATIVE_REVIEWER_NAME,
    STRICT_REVIEWER_NAME,
    SENIOR_REVIEWER_NAME,
]

TOP_LOGIC_MODEL = "opencode/claude-opus-4-8"
TOP_CODE_MODEL = "opencode/qwen3.6-plus"
TOP_STRICT_REVIEW_MODEL = "opencode/gpt-5.5"
TOP_ALTERNATIVE_REVIEW_MODEL = "opencode/gemini-3.5-flash"

LOCAL_ARCHITECT_MODEL = "ollama/qwen3.6:27b-mlx"
LOCAL_CODER_MODEL = "ollama/qwen3.5:9b-mlx"

PRO_ARCHITECT_NAME = PRO_PREFIX + ARCHITECT_NAME
CHEAP_ARCHITECT_NAME = CHEAP_PREFIX + ARCHITECT_NAME
LOCAL_ARCHITECT_NAME = LOCAL_PREFIX + ARCHITECT_NAME

PRO_DEVELOPER = PRO_PREFIX + DEVELOPER_NAME
LOCAL_DEVELOPER = LOCAL_PREFIX + DEVELOPER_NAME

TOP_REVIEWERS = [PRO_PREFIX + name for name in REVIEWERS_NAMES]
LOCAL_REVIEWERS = [LOCAL_PREFIX + name for name in REVIEWERS_NAMES]

PRO_ARCHITECT_REVIEWER_NAME = PRO_PREFIX + ARCHITECT_REVIEWER_NAME

REVIEWERS = [
    # Top reviewers, spare no expense.
    make_reviewer(
        PRO_PREFIX + STRICT_REVIEWER_NAME,
        TOP_STRICT_REVIEW_MODEL,
        ReviewerTemplate.STRICT_DIFF,
    ),
    make_reviewer(
        PRO_PREFIX + ALTERNATIVE_REVIEWER_NAME,
        TOP_ALTERNATIVE_REVIEW_MODEL,
        ReviewerTemplate.ALTERNATIVE,
    ),
    make_reviewer(
        PRO_PREFIX + SENIOR_REVIEWER_NAME, TOP_LOGIC_MODEL, ReviewerTemplate.SENIOR
    ),
    # Architect reviewer.
    make_reviewer(
        PRO_ARCHITECT_REVIEWER_NAME,
        TOP_LOGIC_MODEL,
        ReviewerTemplate.ARCHITECT,
    ),
    # Local reviewers.
    make_reviewer(
        LOCAL_PREFIX + STRICT_REVIEWER_NAME,
        LOCAL_ARCHITECT_MODEL,
        ReviewerTemplate.STRICT_DIFF,
    ),
    make_reviewer(
        LOCAL_PREFIX + ALTERNATIVE_REVIEWER_NAME,
        LOCAL_CODER_MODEL,
        ReviewerTemplate.ALTERNATIVE,
    ),
    make_reviewer(
        LOCAL_PREFIX + SENIOR_REVIEWER_NAME,
        LOCAL_ARCHITECT_MODEL,
        ReviewerTemplate.SENIOR,
    ),
]

DEVELOPERS = [
    # Top developer.
    make_developer(
        PRO_DEVELOPER,
        TOP_CODE_MODEL,
        TOP_REVIEWERS,
    ),
    # Local developer.
    make_developer(
        LOCAL_DEVELOPER,
        LOCAL_CODER_MODEL,
        LOCAL_REVIEWERS,
    ),
]

ARCHITECTS = [
    # Only top of the line, spare no expense.
    make_architect(
        PRO_ARCHITECT_NAME,
        TOP_LOGIC_MODEL,
        [PRO_DEVELOPER],
        TOP_REVIEWERS,
    ),
    # Cheap architect, spends least money, medium effort plan.
    make_architect(
        CHEAP_ARCHITECT_NAME,
        TOP_CODE_MODEL,
        [LOCAL_CODER_MODEL, TOP_CODE_MODEL],
        TOP_REVIEWERS + [PRO_ARCHITECT_REVIEWER_NAME],
        additional_rules=[ADD_PLAN_REVIEWER_TEMPLATE],
    ),
    # All local, send nothing.
    make_architect(
        LOCAL_ARCHITECT_NAME,
        LOCAL_ARCHITECT_MODEL,
        [LOCAL_DEVELOPER],
        LOCAL_REVIEWERS,
    ),
]

AGENTS = REVIEWERS + DEVELOPERS + ARCHITECTS
