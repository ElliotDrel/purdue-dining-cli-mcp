# Purdue Dining CLI-MCP

An unofficial, read-only JSON client for published Purdue Dining Court menus and nutrition.

## What it does

The CLI resolves a published menu item, then returns Purdue's serving size, calories, carbs, protein, fat, ingredients, and source URL. It does not write to any service or collect credentials.

```text
python purdue_dining.py candidates --date YYYY-MM-DD --hall HALL|all --query TEXT [--query TEXT ...] [--meal MEAL]
python purdue_dining.py item --id ITEM_ID
```

Both commands emit JSON only. `--hall all` discovers the current Dining Courts from Purdue's locations response. Python 3.11+ is the only dependency.

## Data source

The client reads Purdue Housing and Food Services' public menu API:

- `https://api.hfs.purdue.edu/menus/v2/locations`
- `https://api.hfs.purdue.edu/menus/v2/locations/{hall}/{YYYY-MM-DD}`
- `https://api.hfs.purdue.edu/menus/v2/items/{item-id}`

This is an independent project. It is not affiliated with Purdue University or Purdue Housing and Food Services. The API is undocumented, so its schema and availability can change without notice.

Use the source politely. Query only the menu items needed for a meal and do not use this project for bulk collection or high-frequency polling.

## Development

```text
python -m unittest discover -s tests -v
python -m py_compile purdue_dining.py
```

## License

[MIT](LICENSE)
