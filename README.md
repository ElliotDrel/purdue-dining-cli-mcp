# Purdue Dining food skill

A standalone Hermes skill for finding published Purdue Dining Court menu items and their nutrition. The repository contains one installable skill folder plus fixtures that verify its public-data contract.

## Install

Copy [`skills/purdue-dining-food/`](skills/purdue-dining-food/) into your Hermes `skills/` directory. That single folder contains every runtime file the skill needs.

## Contents

- `skills/purdue-dining-food/SKILL.md` — the agent procedure.
- `skills/purdue-dining-food/scripts/purdue_dining.py` — the read-only lookup script.
- `tests/` — fixture-based regression coverage.

The script reads Purdue Housing and Food Services' public menu API. It returns JSON only, makes no writes, and needs no credentials.

```text
python skills/purdue-dining-food/scripts/purdue_dining.py candidates --date YYYY-MM-DD --hall HALL|all --query TEXT [--query TEXT ...] [--meal MEAL]
python skills/purdue-dining-food/scripts/purdue_dining.py item --id ITEM_ID
```

This is an independent project. It is not affiliated with Purdue University or Purdue Housing and Food Services. The API is undocumented, so its schema and availability can change. Query only the menu items needed for a meal. Do not use the source for bulk collection or high-frequency polling.

## Verification

```text
python -m unittest discover -s tests -v
python -m py_compile skills/purdue-dining-food/scripts/purdue_dining.py
```

## License

[MIT](LICENSE)
