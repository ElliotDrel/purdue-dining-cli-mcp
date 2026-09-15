import json
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from purdue_dining import find_candidates
except ModuleNotFoundError:
    find_candidates = None

try:
    from purdue_dining import normalize_item
except ImportError:
    normalize_item = None

try:
    from purdue_dining import main
except ImportError:
    main = None

try:
    from purdue_dining import HfsClient
except ImportError:
    HfsClient = None


FIXTURES = Path(__file__).parent / "fixtures"
SKILL_SCRIPT = Path(__file__).parents[1] / "scripts" / "purdue_dining.py"


class SkillLayoutTests(unittest.TestCase):
    def test_embeds_the_menu_lookup_script_in_the_skill(self):
        self.assertTrue(SKILL_SCRIPT.is_file(), "skill script must be at scripts/purdue_dining.py")


class FixtureClient:
    def __init__(self):
        self.locations_response = self._load("locations.json")
        self.menus = {
            "Earhart": self._load("earhart-menu.json"),
            "Ford": self._load("ford-menu.json"),
        }

    def _load(self, name):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def locations(self):
        return self.locations_response

    def menu(self, hall, date):
        return self.menus[hall]

    def item(self, item_id):
        return self._load("item.json")


class HfsClientTests(unittest.TestCase):
    def test_uses_the_three_live_api_paths(self):
        self.assertIsNotNone(HfsClient, "HfsClient must be implemented")
        requested = []

        def fetch_json(url):
            requested.append(url)
            return {"url": url}

        client = HfsClient(fetch_json=fetch_json)

        self.assertEqual(client.locations(), {"url": "https://api.hfs.purdue.edu/menus/v2/locations"})
        self.assertEqual(
            client.menu("Earhart", "2026-09-14"),
            {"url": "https://api.hfs.purdue.edu/menus/v2/locations/Earhart/2026-09-14"},
        )
        self.assertEqual(
            client.item("item-id"),
            {"url": "https://api.hfs.purdue.edu/menus/v2/items/item-id"},
        )
        self.assertEqual(
            requested,
            [
                "https://api.hfs.purdue.edu/menus/v2/locations",
                "https://api.hfs.purdue.edu/menus/v2/locations/Earhart/2026-09-14",
                "https://api.hfs.purdue.edu/menus/v2/items/item-id",
            ],
        )

    def test_reuses_responses_within_one_cli_process(self):
        requested = []

        def fetch_json(url):
            requested.append(url)
            return {"url": url}

        client = HfsClient(fetch_json=fetch_json)
        client.locations()
        client.locations()
        client.menu("Earhart", "2026-09-14")
        client.menu("Earhart", "2026-09-14")
        client.item("item-id")
        client.item("item-id")

        self.assertEqual(len(requested), 3)


class FindCandidatesTests(unittest.TestCase):
    def test_searches_all_dining_halls_for_chicken_candidates(self):
        self.assertIsNotNone(find_candidates, "find_candidates must be implemented")

        candidates = find_candidates(
            FixtureClient(),
            date="2026-09-14",
            hall="all",
            query="chicken",
        )

        self.assertEqual(
            candidates,
            [
                {
                    "id": "earhart-chicken",
                    "name": "Grilled Chicken Breast",
                    "hall": "Earhart",
                    "meal": "Lunch",
                    "station": "Grill",
                },
                {
                    "id": "ford-no-nutrition",
                    "name": "Chicken Soup",
                    "hall": "Ford",
                    "meal": "Dinner",
                    "station": "Comfort",
                },
                {
                    "id": "ford-chicken",
                    "name": "Chicken Tenders",
                    "hall": "Ford",
                    "meal": "Dinner",
                    "station": "Comfort",
                },
            ],
        )


class NormalizeItemTests(unittest.TestCase):
    def test_returns_tracker_ready_raw_macros_and_source_url(self):
        self.assertIsNotNone(normalize_item, "normalize_item must be implemented")
        item = json.loads((FIXTURES / "item.json").read_text(encoding="utf-8"))

        normalized = normalize_item(item, base_url="https://api.hfs.purdue.edu/menus/v2")

        self.assertEqual(
            normalized,
            {
                "name": "All Beef Hot Dog",
                "source_basis": "per 1 hot dog",
                "source_url": "https://api.hfs.purdue.edu/menus/v2/items/earhart-hot-dog",
                "raw": {"calories": 160, "carbs": 2, "protein": 7, "fat": 13},
                "ingredients": "Beef, water, salt.",
            },
        )

    def test_rejects_an_item_without_complete_nutrition(self):
        item = json.loads((FIXTURES / "item-without-nutrition.json").read_text(encoding="utf-8"))

        with self.assertRaisesRegex(ValueError, "Nutrition is unavailable"):
            normalize_item(item, base_url="https://api.hfs.purdue.edu/menus/v2")


class CliTests(unittest.TestCase):
    def test_candidates_command_emits_only_json(self):
        self.assertIsNotNone(main, "main must be implemented")
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(
                [
                    "candidates",
                    "--date",
                    "2026-09-14",
                    "--hall",
                    "all",
                    "--query",
                    "chicken",
                ],
                client=FixtureClient(),
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(
            [candidate["id"] for candidate in payload["candidates"]],
            ["earhart-chicken", "ford-no-nutrition", "ford-chicken"],
        )

    def test_candidates_command_uses_a_live_client_by_default(self):
        output = StringIO()
        with patch("purdue_dining.HfsClient", return_value=FixtureClient()):
            try:
                with redirect_stdout(output):
                    exit_code = main(
                        ["candidates", "--date", "2026-09-14", "--hall", "Earhart", "--query", "hot dog"]
                    )
            except RuntimeError:
                exit_code = None

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(output.getvalue())["candidates"][0]["id"], "earhart-hot-dog")

    def test_multiple_queries_share_one_agent_command(self):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "candidates",
                    "--date",
                    "2026-09-14",
                    "--hall",
                    "all",
                    "--query",
                    "chicken",
                    "--query",
                    "hot dog",
                ],
                client=FixtureClient(),
            )

        self.assertEqual(exit_code, 0)
        candidates = json.loads(output.getvalue())["candidates"]
        self.assertEqual(
            [candidate["id"] for candidate in candidates["chicken"]],
            ["earhart-chicken", "ford-no-nutrition", "ford-chicken"],
        )
        self.assertEqual([candidate["id"] for candidate in candidates["hot dog"]], ["earhart-hot-dog"])

    def test_unknown_hall_returns_a_json_error(self):
        output = StringIO()
        try:
            with redirect_stdout(output):
                exit_code = main(
                    ["candidates", "--date", "2026-09-14", "--hall", "Missing", "--query", "chicken"],
                    client=FixtureClient(),
                )
        except ValueError:
            exit_code = None

        self.assertEqual(exit_code, 2)
        self.assertEqual(json.loads(output.getvalue())["error"]["code"], "unknown_hall")

    def test_item_command_emits_tracker_ready_json(self):
        output = StringIO()
        try:
            with redirect_stdout(output):
                exit_code = main(["item", "--id", "earhart-hot-dog"], client=FixtureClient())
        except SystemExit as error:
            exit_code = error.code

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            json.loads(output.getvalue()),
            {
                "item": {
                    "name": "All Beef Hot Dog",
                    "source_basis": "per 1 hot dog",
                    "source_url": "https://api.hfs.purdue.edu/menus/v2/items/earhart-hot-dog",
                    "raw": {"calories": 160, "carbs": 2, "protein": 7, "fat": 13},
                    "ingredients": "Beef, water, salt.",
                }
            },
        )


if __name__ == "__main__":
    unittest.main()
