# Purdue Dining agent food-logging plan

## Decision

Build a small, private JSON CLI for the existing food logging skill. Do not build an MCP in v1.

The CLI reads Purdue's live menu data. The food logging skill keeps ownership of portion estimates, macro calculation, approval, and Carb Manager writes.

## Data

Use Purdue Housing and Food Services' public API:

- `GET https://api.hfs.purdue.edu/menus/v2/locations/{hall}/{YYYY-MM-DD}`
- `GET https://api.hfs.purdue.edu/menus/v2/items/{item-id}`

Use live requests. Do not add caching, configuration, or a location directory in v1.

## CLI contract

```text
purdue-dining candidates --date YYYY-MM-DD --hall HALL --query TEXT [--meal MEAL]
purdue-dining item --id ITEM_ID
```

Both commands write JSON to stdout and no human-formatted output.

`candidates` returns matching item IDs with name, meal, and station. It reads one hall's menu and does not fetch nutrition for every match.

`item` returns the selected item's name, serving size, calories, carbs, protein, fat, ingredients, and its exact Purdue item URL as `source_url`.

Errors use JSON with a stable `code` for an unknown hall, unavailable menu, empty match, or unavailable nutrition.

## Food logging flow

1. The food skill freezes the log date and identifies a hall, probable dish, and optional meal.
2. It calls `candidates`, then selects the matching menu item from its meal and station context.
3. It calls `item` and records Purdue's serving basis, raw macros, and `source_url` in `tracker_nutrition.json`.
4. The food skill estimates only the portion multiplier.
5. `compute_macros.py` calculates rounded item macros and totals.
6. Elliot approves the usual Carb Manager review before any write.

## Build and verification

1. Save fixtures for a menu, a nutrition panel, and an unavailable-nutrition response.
2. Write failing tests for candidate filtering and normalized item output.
3. Implement the two commands until the tests pass.
4. Add the skill instructions that call the commands during dining-hall meal logging.
5. Verify a live menu lookup and item lookup without creating a Carb Manager entry.

## Deferred

Defer an MCP wrapper until the CLI has proved insufficient for the food workflow.
