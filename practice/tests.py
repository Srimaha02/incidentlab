from django.test import SimpleTestCase
from django.urls import reverse

from .loader import all_scenarios, get_scenario, ordered_scenarios
from .scoring import compute_score


class LoaderTests(SimpleTestCase):

    def test_all_scenarios_loaded(self):
        scenarios = all_scenarios()

        self.assertEqual(len(scenarios), 5)

    def test_required_scenario_exists(self):
        scenario = get_scenario("wrong-port-502")

        self.assertIsNotNone(scenario)
        self.assertEqual(
            scenario["title"],
            "502 right after the deploy",
        )

    def test_scenarios_are_ordered(self):
        scenarios = ordered_scenarios()

        self.assertEqual(
            scenarios[0]["difficulty"],
            "easy",
        )


class ScoringTests(SimpleTestCase):

    def test_full_score(self):
        score = compute_score(
            points=100,
            hints_used=0,
            wrong_attempts=0,
        )

        self.assertEqual(score, 100)

    def test_wrong_answer_penalty(self):
        score = compute_score(
            points=100,
            hints_used=0,
            wrong_attempts=1,
        )

        self.assertEqual(score, 75)

    def test_hint_penalty(self):
        score = compute_score(
            points=100,
            hints_used=1,
            wrong_attempts=0,
        )

        self.assertEqual(score, 75)

    def test_minimum_score(self):
        score = compute_score(
            points=100,
            hints_used=10,
            wrong_attempts=10,
        )

        self.assertEqual(score, 10)


class PracticeViewTests(SimpleTestCase):

    def test_home_page_loads(self):
        response = self.client.get(
            reverse("home")
        )

        self.assertEqual(response.status_code, 200)

    def test_scenario_page_loads(self):
        response = self.client.get(
            reverse(
                "scenario",
                kwargs={
                    "slug": "wrong-port-502"
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_unknown_scenario_returns_404(self):
        response = self.client.get(
            reverse(
                "scenario",
                kwargs={
                    "slug": "does-not-exist"
                },
            )
        )

        self.assertEqual(response.status_code, 404)