from django.shortcuts import render

from .engine import analyze, fallback_summary
from .ai import explain


def home(request):
    context = {
        "text": "",
        "kind": "",
        "findings": [],
        "summary": "",
        "ai_result": None,
        "finding_rows": [],
    }

    if request.method == "POST":
        text = request.POST.get("text", "")
        selected_kind = request.POST.get("kind", "")

        kind, findings = analyze(
            text,
            selected_kind or None,
        )

        ai_result = explain(
    findings,
    text,
    "claude-sonnet-5-5",
)

        finding_rows = []

        for finding in findings:
            ai_text = ""

            if ai_result:
                ai_text = ai_result["explanations"].get(
                    finding.rule_id,
                    "",
                )

            finding_rows.append(
                {
                    "finding": finding,
                    "ai_text": ai_text,
                }
            )

        context.update(
            {
                "text": text,
                "kind": kind or "",
                "findings": findings,
                "finding_rows": finding_rows,
                "summary": (
                    fallback_summary(kind, findings)
                    if kind
                    else "Could not detect the file type."
                ),
                "ai_result": ai_result,
            }
        )

    return render(
        request,
        "doctor/home.html",
        context,
    )