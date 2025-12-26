import time
from datetime import datetime

import httpx

from app.config import (
    BASE_PARAMS,
    MIN_PRICE,
    PROPERTY_TYPES,
    TEMPORARY_RENTAL_KEYWORDS,
)
from app.constants.wallapop import HEADERS
from app.db import SessionLocal, init_db
from app.services.sync import sync_listings


def is_temporary_rental(item: dict) -> bool:
    """Check if listing is a temporary rental"""
    title = item.get("title", "").lower()
    description = item.get("description", "").lower()
    text = f"{title} {description}"
    return any(keyword in text for keyword in TEMPORARY_RENTAL_KEYWORDS)


def simplify_items(items: list[dict]) -> list[dict]:
    """Simplify items by removing unnecessary fields"""
    for item in items:
        item.pop("id", None)
        item.pop("user_id", None)
        item.pop("category_id", None)
        item.pop("shipping", None)
        item.pop("bump", None)
        item.pop("is_favoriteable", None)
        item.pop("is_refurbished", None)
        item.pop("is_top_profile", None)
        item.pop("has_warranty", None)
        item.pop("favorited", None)
        item.pop("taxonomy", None)

        if "price" in item and isinstance(item["price"], dict):
            item["price"] = item["price"].get("amount", 0)

        item["images"] = [img["urls"]["big"] for img in item.get("images", [])]

        if "created_at" in item:
            item["created_at"] = datetime.fromtimestamp(
                item["created_at"] / 1000
            ).isoformat()
        if "modified_at" in item:
            item["modified_at"] = datetime.fromtimestamp(
                item["modified_at"] / 1000
            ).isoformat()

    return items


def fetch_all_pages(
    params_base: dict, headers: dict, max_pages: int = 10
) -> list[dict]:
    """Get all paginated results from API"""
    all_items = []
    params = params_base.copy()
    page = 1

    with httpx.Client(headers=headers) as client:
        while page <= max_pages:
            print(f"  Page {page}...", end=" ")
            response = client.get(
                "https://api.wallapop.com/api/v3/search", params=params
            )

            if response.status_code != 200:
                print(f"Error {response.status_code}")
                break

            data = response.json()
            items = data["data"]["section"]["payload"]["items"]

            if not items:
                print("No more results")
                break

            all_items.extend(items)
            print(f"{len(items)} items (total: {len(all_items)})")

            next_page = data.get("meta", {}).get("next_page")
            if not next_page:
                break

            params = {"next_page": next_page}
            page += 1

    return all_items


def process_property_type(property_type: str, headers: dict, db) -> dict:
    """Process property type and save results"""
    print(f"\n{'=' * 60}")
    print(f"Processing {property_type}s...")
    print(f"{'=' * 60}")

    params = {**BASE_PARAMS, "type": property_type}
    items = fetch_all_pages(params, headers, max_pages=10)

    original_count = len(items)
    items = [item for item in items if not is_temporary_rental(item)]
    filtered_temp = original_count - len(items)

    if filtered_temp > 0:
        print(f"  Filtered out {filtered_temp} temporary rental(s)")

    items = simplify_items(items)

    original_count = len(items)
    items = [item for item in items if item.get("price", 0) >= MIN_PRICE]
    filtered_price = original_count - len(items)

    if filtered_price > 0:
        print(f"  Filtered out {filtered_price} item(s) below {MIN_PRICE}E")

    # Sync with DB and get changes
    changes = sync_listings(db, property_type, items)

    # Print new listings
    if changes["new"]:
        print(f"\n  NEW ({len(changes['new'])}):")
        for item in changes["new"]:
            print(f"    + {item.get('title', '?')[:50]} - {item.get('price', '?')}€")

    # Print updated listings
    if changes["updated"]:
        print(f"\n  UPDATED ({len(changes['updated'])}):")
        for item in changes["updated"]:
            print(f"    ~ {item.get('title', '?')[:50]} - {item.get('price', '?')}€")

    # Print removed listings
    if changes["removed"]:
        print(f"\n  REMOVED ({len(changes['removed'])}):")
        for slug in changes["removed"]:
            print(f"    - {slug}")

    if not changes["new"] and not changes["updated"] and not changes["removed"]:
        print("\n  No changes")

    return {
        "property_type": property_type,
        "total": len(items),
        "filtered_temporary": filtered_temp,
        "filtered_price": filtered_price,
        "new": len(changes["new"]),
        "updated": len(changes["updated"]),
        "removed": len(changes["removed"]),
    }


def refresh_all_listings() -> dict:
    """Update all listings from Wallapop"""
    init_db()
    overall_start = time.time()
    results = []

    db = SessionLocal()
    try:
        for property_type in PROPERTY_TYPES:
            result = process_property_type(property_type, HEADERS, db)
            results.append(result)
    finally:
        db.close()

    total_time = time.time() - overall_start
    print(f"\n{'=' * 60}")
    print(f"Process completed in {total_time:.2f}s!")
    print(f"{'=' * 60}")

    return {
        "success": True,
        "duration_seconds": round(total_time, 2),
        "results": results,
    }
