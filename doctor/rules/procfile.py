import re

from .base import Finding, rule


def _web_line(ctx):
    for i, line in enumerate(ctx.lines, 1):
        if line.strip().startswith("web:"):
            return i, line.strip()[4:].strip()

    return None, None


@rule("procfile")
def pf001_web_process(ctx):
    i, cmd = _web_line(ctx)

    if i is None:
        return [
            Finding(
                "PF001",
                "high",
                None,
                "No 'web:' process defined",
                "Beanstalk starts the process named 'web' to serve traffic.",
                "Add: `web: gunicorn --bind :8000 config.wsgi:application`.",
            )
        ]

    m = re.search(
        r"(?:--bind|-b)[=\s]+:?(\\d+)",
        cmd,
    )

    if m and m.group(1) != "8000":
        return [
            Finding(
                "PF001",
                "high",
                i,
                f"Gunicorn binds to port {m.group(1)}, not 8000",
                "On the Beanstalk Python platform nginx forwards to port 8000.",
                "Change the bind to `:8000` and redeploy.",
            )
        ]

    return []


@rule("procfile")
def pf002_workers(ctx):
    i, cmd = _web_line(ctx)

    if i is None:
        return []

    m = re.search(
        r"(?:--workers|-w)[=\s]+(\d+)",
        cmd,
    )

    if m and int(m.group(1)) > 4:
        return [
            Finding(
                "PF002",
                "low",
                i,
                f"{m.group(1)} gunicorn workers",
                "Each worker uses its own memory. On a small instance this can cause OOM kills.",
                "Start with 2 workers plus a few threads and watch memory metrics.",
            )
        ]

    return []