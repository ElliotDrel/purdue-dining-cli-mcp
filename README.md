# Purdue Dining food skill

A standalone Hermes skill for finding published Purdue Dining Court menu items and their nutrition. The repository contains one skill, its helper script, and fixtures that verify its public-data contract.

## Contents

- `SKILL.md` — the agent procedure.
- `scripts/purdue_dining.py` — the read-only lookup script.
- `tests/` — fixture-based regression coverage.

The script reads Purdue Housing and Food Services' public menu API. It returns JSON only, makes no writes, and needs no credentials.

```text
python scripts/purdue_dining.py candidates --date YYYY-MM-DD --hall HALL|all --query TEXT [--query TEXT ...] [--meal MEAL]
python scripts/purdue_dining.py item --id ITEM_ID
```

This is an independent project. It is not affiliated with Purdue University or Purdue Housing and Food Services. The API is undocumented, so its schema and availability can change. Query only the menu items needed for a meal. Do not use the source for bulk collection or high-frequency polling.

## Verification

```text
python -m unittest discover -s tests -v
python -m py_compile scripts/purdue_dining.py
```

## License

[MIT](LICENSE)
