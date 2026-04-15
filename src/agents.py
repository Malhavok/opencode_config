from .roles import ReviewerTemplate, make_architect, make_developer, make_reviewer

ARCHITECT_NAME = "architect"
DEVELOPER_NAME = "developer"
STRICT_REVIEWER_NAME = "reviewer-strict-diff"
ALTERNATIVE_REVIEWER_NAME = "reviewer-alternative"
SENIOR_REVIEWER_NAME = "reviewer-senior"

TOP_LOGIC_MODEL = "opencode/claude-opus-4-6"
TOP_CODE_MODEL = "opencode/claude-sonnet-4-6"
TOP_STRICT_REVIEW_MODEL = "opencode/gpt-5.3-codex"
TOP_ALTERNATIVE_REVIEW_MODEL = "opencode/gemini-3-flash"

FREE_MODEL_1 = "opencode/big-pickle"
FREE_MODEL_2 = "opencode/nemotron-3-super-free"
FREE_MODEL_3 = "opencode/minimax-m2.5-free"


PRO_PREFIX = "pro-"
FREE_PREFIX = "free-"

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
    make_developer(
        PRO_PREFIX + DEVELOPER_NAME,
        TOP_CODE_MODEL,
        TOP_REVIEWERS,
    ),
    # Free developer.
    make_developer(
        FREE_PREFIX + DEVELOPER_NAME,
        FREE_MODEL_1,
        FREE_REVIEWERS,
    ),
]

ARCHITECTS = [
    make_architect(
        PRO_PREFIX + ARCHITECT_NAME,
        TOP_LOGIC_MODEL,
        [PRO_PREFIX + DEVELOPER_NAME],
        TOP_REVIEWERS,
    ),
    make_architect(
        FREE_PREFIX + ARCHITECT_NAME,
        FREE_MODEL_2,
        [FREE_PREFIX + DEVELOPER_NAME],
        FREE_REVIEWERS,
    ),
]

AGENTS = REVIEWERS + DEVELOPERS + ARCHITECTS
