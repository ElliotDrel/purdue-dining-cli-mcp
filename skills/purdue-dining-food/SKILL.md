---
name: purdue-dining-food
description: Find Purdue dining food nutrition for meal logging.
---

# Purdue Dining food lookup

Use this skill for food served in a Purdue Dining Court. It supplies the published serving basis and raw macros for the existing food logging review.

## Procedure

1. Freeze the food-log date before any lookup.
2. Identify the likely dining hall, dish name, and meal from the photo or description.
3. From the repository root, run:

   ```text
   python purdue_dining.py candidates --date YYYY-MM-DD --hall HALL|all --query TEXT [--query TEXT ...] [--meal MEAL]
   ```

4. Select a candidate using hall, meal, station, and name. If the description does not establish a hall, use `--hall all`.
5. Run:

   ```text
   python purdue_dining.py item --id ITEM_ID
   ```

6. Copy `source_basis`, `raw`, and `source_url` from the JSON response into `tracker_nutrition.json`.
7. Estimate only the portion multiplier. Run `compute_macros.py`, show the normal approval review, and log only after approval.

## Limits

- Do not use the CLI for retail food or a dish absent from the published menu.
- Do not fetch nutrition for every search candidate.
- Do not round or multiply the returned raw macros. The food workflow owns that calculation.
- A JSON `error` means Purdue did not provide usable menu or nutrition data. Follow the existing fallback process.
