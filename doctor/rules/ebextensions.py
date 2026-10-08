import re

from .base import Finding, rule


SECRET_NAME = re.compile(
    r"(PASSWORD|SECRET|API_?KEY|TOKEN|ACCESS_?KEY)",
    re.I,
)


def _options(data):
    """Turn option_settings into (namespace, option, value)."""

    out = []

    block = data.get("option_settings") if isinstance(data, dict) else None

    if isinstance(block, dict):
        for ns, opts in block.items():
            if isinstance(opts, dict):
                for k, v in opts.items():
                    out.append((str(ns), str(k), v))

    elif isinstance(block, list):
        for item in block:
            if isinstance(item, dict):
                out.append(
                    (
                        str(item.get("namespace", "")),
                        str(
                            item.get(
                                "option_name",
                                item.get("OptionName", ""),
                            )
                        ),
                        item.get(
                            "value",
                            item.get("Value"),
                        ),
                    )
                )

    return out


@rule("ebextensions")
def eb001_yaml(ctx):
    out = []

    # YAML does not allow tabs for indentation.
    for i, line in enumerate(ctx.lines, 1):
        if "\t" in line:
            out.append(
                Finding(
                    "EB001",
                    "high",
                    i,
                    "Tab characters in YAML",
                    "YAML only allows spaces for indentation. Tabs can make Beanstalk reject the file.",
                    "Replace tabs with spaces, using consistent indentation.",
                )
            )
            break

    # Also report parser errors if the YAML parser failed.
    if ctx.parse_error:
        out.append(
            Finding(
                "EB001",
                "high",
                None,
                "YAML could not be parsed",
                f"Parser said: {ctx.parse_error[:160]}",
                "Check indentation and verify every key has a colon followed by a value.",
            )
        )

    return out


@rule("ebextensions")
def eb002_migrate_leader(ctx):
    out = []

    cc = (
        ctx.data.get("container_commands")
        if isinstance(ctx.data, dict)
        else None
    )

    if isinstance(cc, dict):
        for name, spec in cc.items():

            cmd = (
                str(spec.get("command", ""))
                if isinstance(spec, dict)
                else ""
            )

            if (
                "migrate" in cmd
                and not (
                    isinstance(spec, dict)
                    and spec.get("leader_only")
                )
            ):
                out.append(
                    Finding(
                        "EB002",
                        "medium",
                        None,
                        f"'{name}' runs migrate without leader_only",
                        "Several instances migrating at once can conflict or run migrations repeatedly.",
                        "Add `leader_only: true` to this container command.",
                    )
                )

    return out


@rule("ebextensions")
def eb003_health_path(ctx):
    if (
        not isinstance(ctx.data, dict)
        or "option_settings" not in ctx.data
    ):
        return []

    if any(
        option == "HealthCheckPath"
        for _, option, _ in _options(ctx.data)
    ):
        return []

    return [
        Finding(
            "EB003",
            "medium",
            None,
            "No HealthCheckPath configured",
            "The default path is '/', which may redirect, require login, or be expensive.",
            "Set `HealthCheckPath: /health/` under the Elastic Beanstalk environment settings.",
        )
    ]


@rule("ebextensions")
def eb004_secrets(ctx):
    out = []

    for namespace, option, value in _options(ctx.data):

        if SECRET_NAME.search(option) and value not in (None, ""):
            out.append(
                Finding(
                    "EB004",
                    "high",
                    None,
                    f"Secret-like option '{option}' stored in configuration",
                    "This file is committed to Git. Anyone with repository access can read the value.",
                    "Remove it and set the value through environment configuration instead.",
                )
            )

    return out