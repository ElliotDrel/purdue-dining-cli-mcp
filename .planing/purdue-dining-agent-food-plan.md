# Purdue Dining agent food-logging plan

## Decision

Build a food-logging skill backed by a private, JSON-only CLI. Do not build an MCP in the first release.

The product serves Hermes agents. Elliot does not need a human-facing terminal interface. The CLI exists as a stable, testable boundary between Purdue's live dining data and the existing Carb Manager approval flow.

## Data source

Use Purdue Housing and Food Services' public, unauthenticated menu API:

- `GET https://api.hfs.purdue.edu/menus/v2/locations`
- `GET https://api.hfs.purdue.edu/menus/v2/locations/{hall}/{YYYY-MM-DD}`
- `GET https://api.hfs.purdue.edu/menus/v2/items/{item-id}`

The menu endpoint supplies meal, station, item ID, vegetarian/vegan flags, allergen flags, and nutrition availability. The item endpoint supplies serving size, calories, carbohydrate, protein, fat, ingredients, and allergens.

The API is undocumented. Treat it as a polite live read source. Do not cache in the first release because dining menus can change.

## Agent interface

Expose only these private commands:

```text
purdue-dining candidates --date YYYY-MM-DD --hall HALL --meal MEAL --query TEXT
purdue-dining item --id ITEM_ID
```

Both commands emit JSON only. They must not prompt, colorize output, or produce human-formatted tables.

### `candidates`

1. Retrieves the live menu for the requested hall and frozen food-log date.
2. Filters by optional meal, dish-name query, vegetarian/vegan flag, and excluded allergens.
3. Returns a candidate list containing the item ID, item name, hall, meal, station, `nutrition_ready`, and the exact menu source URL.
4. Returns a structured error when the hall, date, or menu cannot be resolved.

### `item`

1. Retrieves one confirmed item by item ID.
2. Normalizes serving size, calories, carbs, protein, fat, ingredients, and positive allergens.
3. Returns the exact Purdue item API URL as `source_url`.
4. Returns a structured error if nutrition is unavailable.

## Food logging flow

1. Identify the dining hall, meal slot, frozen date, and probable dish from Elliot's meal photo or description.
2. Call `candidates` to find Purdue's exact published item.
3. Select the correct candidate from its hall, meal, and station context.
4. Call `item` for nutrition only after selecting a candidate.
5. Write its listed serving size and raw macro values into `tracker_nutrition.json`.
6. Use photo evidence only for the portion multiplier. The existing food flow remains responsible for portion estimation.
7. Run `compute_macros.py`. It remains the sole authority for multiplication, rounding, and totals.
8. Show Elliot the normal Carb Manager approval review with Purdue's item API URL in Sources.
9. Log to Carb Manager only after explicit approval.

The client never writes to Carb Manager. It also never replaces the existing approval gate.

## Repository shape

```text
purdue-dining-cli-mcp/
├── purdue_dining.py          # API client and normalized data model
├── cli.py                    # candidates/item JSON interface
├── tests/
│   ├── fixtures/             # saved HFS responses
│   └── test_cli.py
└── .planing/
    └── purdue-dining-agent-food-plan.md
```

The actual package layout can change if tests demonstrate a clearer boundary. The public behavior above is the contract.

## Implementation order

1. Write fixtures for a published menu, an item nutrition panel, an unpublished menu, and an API error.
2. Add a red test for `candidates` filtering an exact item by hall, meal, and query.
3. Implement the minimal HFS API client needed to pass it.
4. Add a red test for normalized `item` nutrition output and the source URL.
5. Implement `item`.
6. Add tests for malformed dates, unknown halls, missing nutrition, allergen filtering, and empty search results.
7. Create the narrow Hermes skill that invokes these commands during food logging.
8. Run live verification against a current Purdue menu and one item detail endpoint.
9. Run the existing food logging workflow through its proposed-entry stage. Do not create a Carb Manager entry during integration testing.

## Deferred work

- MCP wrapper.
- Human-readable CLI output.
- Persistent caching.
- Menu recommendation or meal planning.
- Carb Manager writes.
- Any non-Purdue dining data source.

An MCP wrapper becomes worthwhile only after repeated food-agent usage shows that direct tool calls are materially easier than the JSON CLI boundary.
