# Purdue Dining CLI-MCP

An agent-facing, read-only Purdue Dining client for the food logging workflow.

## Scope

The first release is a private JSON CLI used by a Hermes skill. It resolves a published Purdue Dining menu item, then returns Purdue's serving size, calories, carbs, protein, fat, ingredients, allergens, and source URL for Carb Manager review.

The project does not create Carb Manager entries. The existing food logging workflow remains responsible for portion estimates, macro computation, user approval, and logging.

## Data source

Purdue Housing and Food Services' public menu API:

- `https://api.hfs.purdue.edu/menus/v2/locations`
- `https://api.hfs.purdue.edu/menus/v2/locations/{hall}/{YYYY-MM-DD}`
- `https://api.hfs.purdue.edu/menus/v2/items/{item-id}`

The API is undocumented. Treat it as a polite, live read source and keep the client narrow.

## Initial interface

```text
purdue-dining candidates --date YYYY-MM-DD --hall HALL --meal MEAL --query TEXT
purdue-dining item --id ITEM_ID
```

Both commands will emit JSON only. A future MCP wrapper is out of scope until the CLI proves useful.

## Repository status

This repository is local-only while development is underway. It has no remote yet. Connect it to the company GitHub organization after the first usable version is complete.
