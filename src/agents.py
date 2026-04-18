from .consts import CHEAP_PREFIX, FREE_PREFIX, MEDIUM_PREFIX, PRO_PREFIX
from .roles import ReviewerTemplate, make_architect, make_developer, make_reviewer

ARCHITECT_NAME = "architect"
DEVELOPER_NAME = "developer"
STRICT_REVIEWER_NAME = "reviewer-strict-diff"
ALTERNATIVE_REVIEWER_NAME = "reviewer-alternative"
SENIOR_REVIEWER_NAME = "reviewer-senior"

TOP_LOGIC_MODEL = "opencode/claude-opus-4-7"
TOP_CODE_MODEL = "opencode/claude-sonnet-4-6"
TOP_STRICT_REVIEW_MODEL = "opencode/gpt-5.3-codex"
TOP_ALTERNATIVE_REVIEW_MODEL = "opencode/gemini-3-flash"

MEDIUM_CODE_MODEL = "opencode/glm-5.1"
CHEAP_CODE_MODEL = "opencode/qwen3.6-plus"

FREE_MODEL_1 = "opencode/big-pickle"
FREE_MODEL_2 = "opencode/minimax-m2.5-free"
FREE_MODEL_3 = "opencode/nemotron-3-super-free"

PRO_ARCHITECT_NAME = PRO_PREFIX + ARCHITECT_NAME
MEDIUM_ARCHITECT_NAME = MEDIUM_PREFIX + ARCHITECT_NAME
CHEAP_ARCHITECT_NAME = CHEAP_PREFIX + ARCHITECT_NAME
FREE_ARCHITECT_NAME = FREE_PREFIX + ARCHITECT_NAME

PRO_DEVELOPER = PRO_PREFIX + DEVELOPER_NAME
MEDIUM_DEVELOPER = MEDIUM_PREFIX + DEVELOPER_NAME
CHEAP_DEVELOPER = CHEAP_PREFIX + DEVELOPER_NAME
FREE_DEVELOPER = FREE_PREFIX + DEVELOPER_NAME


TOP_REVIEWERS = [
    PRO_PREFIX + STRICT_REVIEWER_NAME,
    PRO_PREFIX + ALTERNATIVE_REVIEWER_NAME,
    PRO_PREFIX + SENIOR_REVIEWER_NAME,
]

FREE_REVIEWERS = [
    FREE_PREFIX + STRICT_REVIEWER_NAME,
    FREE_PREFIX + ALTERNATIVE_REVIEWER_NAME,
    FREE_PREFIX + SENIOR_REVIEWER_NAME,
]

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
    # Free reviewers, you "pay" for what you get.
    make_reviewer(
        FREE_PREFIX + STRICT_REVIEWER_NAME,
        FREE_MODEL_1,
        ReviewerTemplate.STRICT_DIFF,
    ),
    make_reviewer(
        FREE_PREFIX + ALTERNATIVE_REVIEWER_NAME,
        FREE_MODEL_2,
        ReviewerTemplate.ALTERNATIVE,
    ),
    make_reviewer(
        FREE_PREFIX + SENIOR_REVIEWER_NAME, FREE_MODEL_3, ReviewerTemplate.SENIOR
    ),
]

DEVELOPERS = [
    # Top developer.
    # All of them use top reviewers, as reviews
    # are usually cheap and are to provide the most feedback.
    make_developer(
        PRO_DEVELOPER,
        TOP_CODE_MODEL,
        TOP_REVIEWERS,
    ),
    # Medium developer.
    make_developer(
        MEDIUM_DEVELOPER,
        MEDIUM_CODE_MODEL,
        TOP_REVIEWERS,
    ),
    # Cheap developer.
    make_developer(
        CHEAP_DEVELOPER,
        CHEAP_CODE_MODEL,
        TOP_REVIEWERS,
    ),
    # Free developer.
    # Only this one is using free reviewers,
    # the rest try to do the best work possible.
    make_developer(
        FREE_DEVELOPER,
        FREE_MODEL_1,
        FREE_REVIEWERS,
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
    # All free, spend nothing.
    make_architect(
        FREE_ARCHITECT_NAME,
        FREE_MODEL_1,
        [FREE_DEVELOPER],
        FREE_REVIEWERS,
    ),
    # Medium architect, spends some money, high effort plan.
    make_architect(
        MEDIUM_ARCHITECT_NAME,
        TOP_LOGIC_MODEL,
        [MEDIUM_DEVELOPER, PRO_DEVELOPER],
        TOP_REVIEWERS,
    ),
    # Cheap architect, spends least money, medium effort plan.
    make_architect(
        CHEAP_ARCHITECT_NAME,
        TOP_CODE_MODEL,
        [FREE_DEVELOPER, CHEAP_DEVELOPER],
        TOP_REVIEWERS,
    ),
]

AGENTS = REVIEWERS + DEVELOPERS + ARCHITECTS
