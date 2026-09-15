---
name: purdue-dining-food
description: Find Purdue Dining meals and source nutrition.
version: 1.0.0
author: Elliot Drel (ElliotDrel), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [purdue, dining, food, nutrition]
    related_skills: [food-nutrition-tracker]
---

# Purdue Dining food lookup

Use this skill with `food-nutrition-tracker` for meals from Purdue Dining Courts. This skill retrieves published serving data and raw macros. The food tracker retains control of portions, review, and Carb Manager writes.

## When to use

- A user names a Purdue Dining Court, or describes food that came from one.
- A user wants to identify a food from a specific dining-court menu.
- A user needs nutrition for an identified Purdue menu item.

Do not use this skill for retail food, off-campus restaurants, or dishes missing from Purdue's published menu.

## Procedure

1. Read the frozen `log_date` from the food-tracker session and identify the named hall, meal, and dishes. The current Dining Courts are Earhart, Ford, Hillenbrand, Wiley, and Windsor.
2. Resolve `scripts/purdue_dining.py` relative to this skill's directory. Use `terminal` to run `python <script> candidates --date YYYY-MM-DD --hall HALL|all --query TEXT [--query TEXT ...] [--meal MEAL]`.
3. Use `--hall all` only when the user did not name a hall. Select each returned item by its hall, meal, station, and exact name.
4. Use `terminal` to run `python <script> item --id ITEM_ID` for every selected item. Do not treat a candidate as nutrition-confirmed until this command succeeds.
5. Copy the returned `source_basis`, `raw`, and `source_url` into `tracker_nutrition.json`. Estimate only the portion multiplier, then let `compute_macros.py` calculate the review values.

## Output contract

- `candidates` emits JSON with published IDs, names, halls, meals, and stations.
- `item` emits JSON with one serving basis, raw calories, carbs, protein, fat, ingredients, and Purdue's exact item URL.
- The script does no writes and needs no credentials.

## Limits

- Purdue's API is public and undocumented. Its structure and availability can change.
- A JSON `error` means Purdue did not provide usable data. Do not invent nutrition. Use the standard food-tracker fallback for that item.
- Do not round or multiply raw macro values. `compute_macros.py` owns all macro arithmetic.

## Verification

A successful lookup has a selected item, an `item` response with all four raw macros, and Purdue's direct `source_url`. The normal food-tracker approval review must occur before logging anything to Carb Manager.
