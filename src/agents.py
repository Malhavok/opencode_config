from .roles import ReviewerTemplate, make_architect, make_developer, make_reviewer

HIGH_LOGIC_MODEL = "opencode/claude-opus-4-6"
HIGH_CODE_MODEL = "opencode/claude-sonnet-4-6"
REVIEW_MODEL_1 = "opencode/gpt-5.3-codex"
REVIEW_MODEL_2 = "opencode/gemini-3-flash"

ARCHITECT_NAME = "architect"
DEVELOPER_NAME = "developer"
REVIEWER_1_NAME = "reviewer-codex"
REVIEWER_2_NAME = "reviewer-gemini"
REVIEWER_3_NAME = "reviewer-opus"


AGENTS = [
    make_architect(
        ARCHITECT_NAME,
        HIGH_LOGIC_MODEL,
        [DEVELOPER_NAME],
        [REVIEWER_1_NAME, REVIEWER_2_NAME, REVIEWER_3_NAME],
    ),
    make_developer(
        DEVELOPER_NAME,
        HIGH_CODE_MODEL,
        [REVIEWER_1_NAME, REVIEWER_2_NAME, REVIEWER_3_NAME],
    ),
    make_reviewer(REVIEWER_1_NAME, REVIEW_MODEL_1, ReviewerTemplate.STRICT_DIFF),
    make_reviewer(REVIEWER_2_NAME, REVIEW_MODEL_2, ReviewerTemplate.ALTERNATIVE),
    make_reviewer(REVIEWER_3_NAME, HIGH_LOGIC_MODEL, ReviewerTemplate.SENIOR),
]
