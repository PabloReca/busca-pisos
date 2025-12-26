from app.config import NOTIFICATION_MAX_PRICE
from app.models.listing import Listing, PropertyType
from app.services.telegram import send_listing_notification


def sync_listings(db, property_type: str, items: list[dict]) -> dict:
    """
    Sync listings with database.
    Returns {new: [...], removed: [...], updated: [...]}
    """
    # Get current listings from database
    stored = {
        listing.web_slug: listing.hash
        for listing in db.query(Listing.web_slug, Listing.hash)
        .filter(Listing.property_type == PropertyType(property_type))
        .all()
    }

    current_slugs = set()
    new_items = []
    updated_items = []

    for item in items:
        slug = item.get("web_slug")
        if not slug:
            continue

        current_slugs.add(slug)
        item_hash = Listing.compute_hash(item)

        if slug not in stored:
            new_items.append(item)
            db.add(Listing.from_dict(item, property_type))
        elif stored[slug] != item_hash:
            updated_items.append(item)
            db.query(Listing).filter(Listing.web_slug == slug).delete()
            db.add(Listing.from_dict(item, property_type))

    # Removed
    stored_slugs = set(stored.keys())
    removed_slugs = stored_slugs - current_slugs

    if removed_slugs:
        db.query(Listing).filter(
            Listing.web_slug.in_(removed_slugs),
            Listing.property_type == PropertyType(property_type),
        ).delete(synchronize_session=False)

    db.commit()

    # Send Telegram notifications for new listings under max price
    for item in new_items:
        price = item.get("price", 0)
        if price and price <= NOTIFICATION_MAX_PRICE:
            send_listing_notification(item)

    return {
        "new": new_items,
        "removed": list(removed_slugs),
        "updated": updated_items,
    }
