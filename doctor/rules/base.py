"""Rule engine core: finding type, registry, and rule decorator."""

from dataclasses import asdict, dataclass


KINDS = (
    "dockerfile",
    "ebextensions",
    "procfile",
    "settings",
)

SEVERITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
}


REGISTRY = {kind: [] for kind in KINDS}


@dataclass
class Finding:
    rule_id: str
    severity: str
    line: int | None
    title: str
    why: str
    fix: str

    def to_dict(self):
        return asdict(self)


class Ctx:
    """What a rule receives: raw text, lines, parsed data."""

    def __init__(self, text, data=None, parse_error=None):
        self.text = text
        self.lines = text.splitlines()
        self.data = data
        self.parse_error = parse_error


def rule(kind):
    def deco(func):
        REGISTRY[kind].append(func)
        return func

    return deco