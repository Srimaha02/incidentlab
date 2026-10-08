"""Runs the rules.

Input is treated purely as TEXT:
never executed, never eval'd.
"""

import re

import yaml

from .rules.base import REGISTRY, SEVERITY_ORDER, Ctx

def detect_kind(text):
    lines = [
        line
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if any(
        re.match(r"^\s*FROM\s+\S+", line, re.I)
        for line in lines
    ):
        return "dockerfile"

    if any(
        line.strip().startswith("web:")
        for line in lines
    ):
        return "procfile"

    if re.search(
        r"^\s*(ALLOWED_HOSTS|DEBUG|SECRET_KEY|SECURE_SSL_REDIRECT)\s*=",
        text,
        re.M,
    ):
        return "settings"

    if re.search(
        r"^\s*(option_settings|container_commands|commands|files|packages)\s*:",
        text,
        re.M,
    ):
        return "ebextensions"

    return None


def _parse_yaml(text):
    try:
        return yaml.safe_load(text), None
    except yaml.YAMLError as e:
        return None, str(e)


def analyze(text, kind=None):
    """
    Returns (kind, findings).

    kind=None means we detect the input automatically.
    """

    kind = kind if kind in REGISTRY else detect_kind(text)

    if kind is None:
        return None, []

    data = err = None

    if kind == "ebextensions":
        data, err = _parse_yaml(text)

    ctx = Ctx(text, data, err)

    findings = []

    for fn in REGISTRY[kind]:
        findings.extend(fn(ctx))

    findings.sort(
        key=lambda f: (
            SEVERITY_ORDER[f.severity],
            f.line or 0,
        )
    )

    return kind, findings


def fallback_summary(kind, findings):
    if not findings:
        return (
            f"No issues found by the {kind} rules. "
            "This does not guarantee the deployment is correct."
        )

    counts = {
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for finding in findings:
        counts[finding.severity] += 1

    return (
        f"Found {len(findings)} issue(s) in your {kind}: "
        f"{counts['high']} high, "
        f"{counts['medium']} medium, "
        f"{counts['low']} low. "
        "Fix the high ones first."
    )