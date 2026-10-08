"""Loads scenario JSON files."""

import json
from functools import lru_cache
from pathlib import Path


SCENARIO_DIR = Path(__file__).parent / "scenarios"

REQUIRED = (
    "slug",
    "title",
    "difficulty",
    "briefing",
    "artifacts",
    "options",
    "explanation",
    "lesson",
    "hints",
    "points",
)

DIFFICULTY_ORDER = {
    "easy": 0,
    "medium": 1,
    "hard": 2,
}


@lru_cache(maxsize=1)
def all_scenarios():
    """Read and validate all scenario JSON files."""

    items = {}

    for file in sorted(SCENARIO_DIR.glob("*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))

        missing = set(REQUIRED) - set(data)

        if missing:
            raise ValueError(
                f"{file.name} is missing fields: {sorted(missing)}"
            )

        items[data["slug"]] = data

    return items


def ordered_scenarios():
    return sorted(
        all_scenarios().values(),
        key=lambda s: (
            DIFFICULTY_ORDER.get(s.get("difficulty"), 9),
            s["title"],
        ),
    )


def get_scenario(slug):
    return all_scenarios().get(slug)


def next_slug(slug):
    scenarios = [s["slug"] for s in ordered_scenarios()]

    if slug in scenarios:
        index = scenarios.index(slug)

        if index + 1 < len(scenarios):
            return scenarios[index + 1]

    return None