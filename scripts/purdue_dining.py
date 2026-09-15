"""Purdue Dining menu helpers."""

import argparse
import json
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE_URL = "https://api.hfs.purdue.edu/menus/v2"


class HfsClient:
    """Small read-only client for Purdue's published HFS menu API."""

    def __init__(self, *, base_url=BASE_URL, fetch_json=None):
        self.base_url = base_url.rstrip("/")
        self._fetch_json = fetch_json or _fetch_json
        self._cache = {}

    def locations(self):
        return self._get(f"{self.base_url}/locations")

    def menu(self, hall, date):
        return self._get(f"{self.base_url}/locations/{quote(hall, safe='')}/{quote(date, safe='')}")

    def item(self, item_id):
        return self._get(f"{self.base_url}/items/{quote(item_id, safe='')}")

    def _get(self, url):
        if url not in self._cache:
            self._cache[url] = self._fetch_json(url)
        return self._cache[url]


def _fetch_json(url):
    request = Request(url, headers={"User-Agent": "PurdueDiningFoodCLI/0.1"})
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def find_candidates(client, *, date, hall, query, meal=None):
    """Return published menu items matching one food query."""
    requested_halls = _resolve_halls(client.locations(), hall)
    query_normalized = query.casefold()
    meal_normalized = meal.casefold() if meal else None
    candidates = []

    for hall_name in requested_halls:
        menu = client.menu(hall_name, date)
        for meal_data in menu.get("Meals", []):
            meal_name = meal_data.get("Name", "")
            if meal_normalized and meal_name.casefold() != meal_normalized:
                continue
            for station in meal_data.get("Stations", []):
                for item in station.get("Items", []):
                    if query_normalized not in item.get("Name", "").casefold():
                        continue
                    candidates.append(
                        {
                            "id": item["ID"],
                            "name": item["Name"],
                            "hall": hall_name,
                            "meal": meal_name,
                            "station": station.get("Name", ""),
                        }
                    )

    return sorted(candidates, key=lambda item: (item["hall"], item["meal"], item["station"], item["name"]))


def normalize_item(item, *, base_url):
    """Return the fields the food logging flow records for one item."""
    values = {entry.get("Name"): entry.get("Value") for entry in item.get("Nutrition", [])}
    serving_size = next(
        (entry.get("LabelValue") for entry in item.get("Nutrition", []) if entry.get("Name") == "Serving Size"),
        None,
    )
    required = {
        "calories": values.get("Calories"),
        "carbs": values.get("Total Carbohydrate"),
        "protein": values.get("Protein"),
        "fat": values.get("Total fat"),
    }
    if not serving_size or any(value is None for value in required.values()):
        raise ValueError(f"Nutrition is unavailable for item: {item.get('Name', item.get('ID', 'unknown'))}")

    return {
        "name": item["Name"],
        "source_basis": f"per {serving_size}",
        "source_url": f"{base_url}/items/{item['ID']}",
        "raw": required,
        "ingredients": item.get("Ingredients", ""),
    }


def _resolve_halls(locations_response, requested_hall):
    dining_halls = [
        location["Name"]
        for location in locations_response.get("Location", [])
        if location.get("Type") == "Dining Courts"
    ]
    if requested_hall.casefold() == "all":
        return dining_halls

    for hall_name in dining_halls:
        if hall_name.casefold() == requested_hall.casefold():
            return [hall_name]
    raise ValueError(f"Unknown dining hall: {requested_hall}")


def main(argv=None, *, client=None):
    """Run the JSON command interface."""
    parser = argparse.ArgumentParser(add_help=False)
    commands = parser.add_subparsers(dest="command", required=True)
    candidates_parser = commands.add_parser("candidates", add_help=False)
    candidates_parser.add_argument("--date", required=True)
    candidates_parser.add_argument("--hall", required=True)
    candidates_parser.add_argument("--query", action="append", required=True)
    candidates_parser.add_argument("--meal")
    item_parser = commands.add_parser("item", add_help=False)
    item_parser.add_argument("--id", required=True)

    args = parser.parse_args(argv)
    client = client or HfsClient()

    try:
        if args.command == "candidates":
            by_query = {
                query: find_candidates(
                    client,
                    date=args.date,
                    hall=args.hall,
                    query=query,
                    meal=args.meal,
                )
                for query in args.query
            }
            payload = by_query[args.query[0]] if len(args.query) == 1 else by_query
            print(json.dumps({"candidates": payload}))
            return 0

        if args.command == "item":
            item = normalize_item(client.item(args.id), base_url=getattr(client, "base_url", BASE_URL))
            print(json.dumps({"item": item}))
            return 0
    except ValueError as error:
        code = "unknown_hall" if str(error).startswith("Unknown dining hall") else "nutrition_unavailable"
        print(json.dumps({"error": {"code": code, "message": str(error)}}))
        return 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
