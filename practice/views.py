from django.http import Http404
from django.shortcuts import render

from .loader import get_scenario, next_slug, ordered_scenarios
from .scoring import compute_score


def home(request):
    scenarios = ordered_scenarios()

    return render(
        request,
        "practice/home.html",
        {
            "scenarios": scenarios,
        },
    )


def scenario(request, slug):
    data = get_scenario(slug)

    if data is None:
        raise Http404("Scenario not found")

    session_key = f"scenario_{slug}"

    state = request.session.get(
        session_key,
        {
            "hints_used": 0,
            "wrong_attempts": 0,
            "answered": False,
            "selected": None,
        },
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "hint":
            state["hints_used"] += 1

        elif action == "answer":
            selected = request.POST.get("option")
            state["selected"] = selected
            state["answered"] = True

            correct = next(
                (
                    option
                    for option in data["options"]
                    if option["id"] == selected
                ),
                None,
            )

            if not correct or not correct.get("correct"):
                state["wrong_attempts"] += 1

        request.session[session_key] = state

    score = compute_score(
        data["points"],
        state["hints_used"],
        state["wrong_attempts"],
    )

    next_scenario = next_slug(slug)

    return render(
        request,
        "practice/scenario.html",
        {
            "scenario": data,
            "state": state,
            "score": score,
            "next_scenario": next_scenario,
        },
    )