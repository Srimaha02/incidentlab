import re

from .base import Finding, rule


SECRET_NAME = re.compile(
    r"(PASSWORD|SECRET|API_?KEY|TOKEN|ACCESS_?KEY)",
    re.I,
)


def _instructions(ctx):
    """Yield (line_number, INSTRUCTION, rest), skipping comments and blank lines."""

    for i, line in enumerate(ctx.lines, 1):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split(None, 1)

        yield (
            i,
            parts[0].upper(),
            parts[1] if len(parts) > 1 else "",
        )


@rule("dockerfile")
def df001_no_expose(ctx):
    if any(
        ins == "EXPOSE"
        for _, ins, _ in _instructions(ctx)
    ):
        return []

    return [
        Finding(
            "DF001",
            "high",
            None,
            "No EXPOSE instruction",
            "Beanstalk's Docker platform reads EXPOSE to know which port to serve.",
            "Add a line such as `EXPOSE 8000` and make your app listen on that port.",
        )
    ]


@rule("dockerfile")
def df002_latest_tag(ctx):
    out = []

    for i, ins, rest in _instructions(ctx):
        if ins != "FROM":
            continue

        image = rest.split()[0] if rest.split() else ""

        if image.lower() == "scratch":
            continue

        if ":" not in image or image.endswith(":latest"):
            out.append(
                Finding(
                    "DF002",
                    "medium",
                    i,
                    "Unpinned base image",
                    "A floating tag can change under you and break a deploy.",
                    "Pin a specific version, for example `python:3.12-slim`.",
                )
            )

    return out


@rule("dockerfile")
def df003_root_user(ctx):
    if any(
        ins == "USER"
        for _, ins, _ in _instructions(ctx)
    ):
        return []

    return [
        Finding(
            "DF003",
            "medium",
            None,
            "Container runs as root",
            "If the app is compromised, the attacker has root inside the container.",
            "Create a user and add `USER appuser` before the CMD line.",
        )
    ]


@rule("dockerfile")
def df004_cache_order(ctx):
    copy_all = install = None

    for i, ins, rest in _instructions(ctx):

        if (
            ins == "COPY"
            and re.match(r"\.\s+\S+", rest)
            and copy_all is None
        ):
            copy_all = i

        if (
            ins == "RUN"
            and "pip install" in rest
            and install is None
        ):
            install = i

    if copy_all and install and copy_all < install:
        return [
            Finding(
                "DF004",
                "low",
                copy_all,
                "Dependencies installed after copying all code",
                "Any code change invalidates the cache, so dependencies are reinstalled.",
                "COPY requirements.txt first, run pip install, and only then COPY the application code.",
            )
        ]

    return []


@rule("dockerfile")
def df005_dev_server(ctx):
    out = []

    for i, ins, rest in _instructions(ctx):
        if (
            ins in ("CMD", "ENTRYPOINT")
            and re.search(r"runserver|flask\s+run", rest)
        ):
            out.append(
                Finding(
                    "DF005",
                    "high",
                    i,
                    "Development server used in production",
                    "The Django/Flask development servers are not suitable for production traffic.",
                    'Use gunicorn, e.g. `CMD ["gunicorn", "--bind", ":8000", "config.wsgi:application"]`.',
                )
            )

    return out


@rule("dockerfile")
def df006_secrets_in_env(ctx):
    out = []

    for i, ins, rest in _instructions(ctx):
        if ins in ("ENV", "ARG"):

            name = re.split(r"[=\s]", rest, 1)[0]

            has_value = (
                "=" in rest
                or len(rest.split()) > 1
            )

            if SECRET_NAME.search(name) and has_value:
                out.append(
                    Finding(
                        "DF006",
                        "high",
                        i,
                        f"Secret '{name}' baked into the image",
                        "Anyone who can pull the image can read the value.",
                        "Remove it and set it as an environment property instead.",
                    )
                )

    return out