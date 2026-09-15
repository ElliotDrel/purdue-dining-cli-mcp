# Purdue Dining food skill plan

## Decision

Ship one standalone `purdue-dining-food` skill folder at `skills/purdue-dining-food/`. Its helper script lives under `skills/purdue-dining-food/scripts/`. Do not publish a separate CLI package or an MCP server.

The skill reads Purdue's live menu data. `food-nutrition-tracker` keeps ownership of portions, macro calculation, approval, and Carb Manager writes.

## Data boundary

Use Purdue Housing and Food Services' public endpoints:

- `GET https://api.hfs.purdue.edu/menus/v2/locations`
- `GET https://api.hfs.purdue.edu/menus/v2/locations/{hall}/{YYYY-MM-DD}`
- `GET https://api.hfs.purdue.edu/menus/v2/items/{item-id}`

Use live requests and cache only within one script run. The script has no credentials, configuration, persistent cache, or write operations.

## Skill contract

The agent resolves `scripts/purdue_dining.py` relative to the installed skill directory.

- `candidates` searches one named Dining Court or all current courts for one or more dish queries.
- `item` returns a selected menu item's serving basis, raw macros, ingredients, and direct Purdue source URL.
- Both commands emit JSON. The script reports unavailable data without inventing nutrition.

## Food flow

1. The food tracker freezes the log date and identifies a hall, meal, and dishes.
2. The Purdue skill finds candidate menu items and confirms each selected item.
3. The food tracker writes Purdue's raw values into its nutrition JSON, estimates portions, runs `compute_macros.py`, and presents the standard review.
4. Carb Manager writes occur only after explicit authorization.

## Verification

1. Keep fixtures and tests for hall discovery, candidate search, item normalization, and missing nutrition.
2. Test the skill-relative script path and run the full suite before publishing.
3. Live-test one candidate lookup and one item lookup without creating a Carb Manager entry.
