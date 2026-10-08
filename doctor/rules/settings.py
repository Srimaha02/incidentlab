import re

from .base import Finding, rule


@rule("settings")
def st001_debug(ctx):
    for i, line in enumerate(ctx.lines, 1):
        if re.search(r"^\s*DEBUG\s*=\s*True\b", line):
            return [
                Finding(
                    "ST001",
                    "high",
                    i,
                    "DEBUG=True in production",
                    "Django exposes detailed error pages when DEBUG is enabled.",
                    "Set DEBUG=False in production.",
                )
            ]

    return []


@rule("settings")
def st002_secret_key(ctx):
    for i, line in enumerate(ctx.lines, 1):
        if re.search(
            r"^\s*SECRET_KEY\s*=\s*['\"]",
            line,
        ):
            return [
                Finding(
                    "ST002",
                    "high",
                    i,
                    "SECRET_KEY hardcoded",
                    "Secrets should not be committed to source control.",
                    "Read SECRET_KEY from an environment variable.",
                )
            ]

    return []


@rule("settings")
def st003_allowed_hosts(ctx):
    for i, line in enumerate(ctx.lines, 1):
        if re.search(
            r"^\s*ALLOWED_HOSTS\s*=\s*\[\s*\]",
            line,
        ):
            return [
                Finding(
                    "ST003",
                    "medium",
                    i,
                    "ALLOWED_HOSTS is empty",
                    "Django rejects requests whose Host header is not allowed.",
                    "Configure ALLOWED_HOSTS for the deployed hostname.",
                )
            ]

    return []


@rule("settings")
def st004_csrf_origins(ctx):
    for i, line in enumerate(ctx.lines, 1):
        if "CSRF_TRUSTED_ORIGINS" in line:
            return []

    return [
        Finding(
            "ST004",
            "medium",
            None,
            "CSRF_TRUSTED_ORIGINS not configured",
            "Cross-origin POST requests may be rejected after deployment.",
            "Configure CSRF_TRUSTED_ORIGINS for the deployed HTTPS origin.",
        )
    ]