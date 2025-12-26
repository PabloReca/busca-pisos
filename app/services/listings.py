from typing import Optional

from app.config import BASE_LAT, BASE_LON
from app.db import SessionLocal
from app.models.listing import Listing
from app.services.geo import haversine_distance


def load_listings() -> list[dict]:
    """Load listings from database"""
    db = SessionLocal()
    try:
        listings_db = db.query(Listing).all()
        listings = []

        for listing in listings_db:
            item = {
                "web_slug": listing.web_slug,
                "property_type": listing.property_type.value,
                "title": listing.title,
                "description": listing.description,
                "price": listing.price,
                "images": listing.images or [],
                "reserved": listing.reserved,
                "location": {
                    "latitude": listing.latitude,
                    "longitude": listing.longitude,
                    "postal_code": listing.postal_code,
                    "city": listing.city,
                    "region": listing.region,
                    "country_code": listing.country_code,
                },
                "type_attributes": {
                    "operation": listing.operation,
                    "surface": listing.surface,
                    "rooms": listing.rooms,
                    "bathrooms": listing.bathrooms,
                },
                "created_at": listing.created_at.isoformat()
                if listing.created_at
                else None,
                "modified_at": listing.modified_at.isoformat()
                if listing.modified_at
                else None,
            }

            # Calculate distance
            if listing.latitude and listing.longitude:
                item["distance_km"] = round(
                    haversine_distance(
                        BASE_LAT, BASE_LON, listing.latitude, listing.longitude
                    ),
                    1,
                )
            else:
                item["distance_km"] = None

            listings.append(item)

        return listings
    except (ValueError, TypeError, RuntimeError, Exception):
        # Database connection error - return empty list
        return []
    finally:
        try:
            db.close()
        except Exception:
            pass


def filter_listings(
    listings: list[dict],
    property_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_rooms: Optional[int] = None,
    max_rooms: Optional[int] = None,
    min_bathrooms: Optional[int] = None,
    max_bathrooms: Optional[int] = None,
    max_distance: Optional[float] = None,
) -> list[dict]:
    """Apply filters to listings"""
    if property_type:
        listings = [
            listing for listing in listings if listing["property_type"] == property_type
        ]
    if min_price is not None:
        listings = [
            listing for listing in listings if listing.get("price", 0) >= min_price
        ]
    if max_price is not None:
        listings = [
            listing for listing in listings if listing.get("price", 0) <= max_price
        ]
    if min_rooms is not None:
        listings = [
            listing for listing in listings if listing.get("rooms", 0) >= min_rooms
        ]
    if max_rooms is not None:
        listings = [
            listing for listing in listings if listing.get("rooms", 0) <= max_rooms
        ]
    if min_bathrooms is not None:
        listings = [
            listing
            for listing in listings
            if listing.get("bathrooms", 0) >= min_bathrooms
        ]
    if max_bathrooms is not None:
        listings = [
            listing
            for listing in listings
            if listing.get("bathrooms", 0) <= max_bathrooms
        ]
    if max_distance is not None:
        listings = [
            listing
            for listing in listings
            if listing.get("distance_km") is not None
            and listing["distance_km"] <= max_distance
        ]

    return listings


def sort_listings(
    listings: list[dict], sort_by: str = "price", sort_order: str = "asc"
) -> list[dict]:
    """Sort listings"""
    reverse = sort_order == "desc"

    if sort_by == "price":
        listings.sort(key=lambda x: x.get("price", 0), reverse=reverse)
    elif sort_by == "distance":
        listings.sort(key=lambda x: x.get("distance_km") or 999, reverse=reverse)
    elif sort_by == "date":
        listings.sort(key=lambda x: x.get("modified_at", ""), reverse=reverse)

    return listings


def get_stats(listings: list[dict]) -> dict:
    """Calculate statistics of listings"""
    prices = [listing["price"] for listing in listings if listing.get("price")]
    rooms = [listing["rooms"] for listing in listings if listing.get("rooms")]
    bathrooms = [
        listing["bathrooms"] for listing in listings if listing.get("bathrooms")
    ]
    distances = [
        listing["distance_km"] for listing in listings if listing.get("distance_km")
    ]

    return {
        "total": len(listings),
        "apartments": len(
            [listing for listing in listings if listing["property_type"] == "apartment"]
        ),
        "houses": len(
            [listing for listing in listings if listing["property_type"] == "house"]
        ),
        "price": {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
        },
        "rooms": {"min": min(rooms) if rooms else 0, "max": max(rooms) if rooms else 0},
        "bathrooms": {
            "min": min(bathrooms) if bathrooms else 0,
            "max": max(bathrooms) if bathrooms else 0,
        },
        "distance": {
            "min": min(distances) if distances else 0,
            "max": max(distances) if distances else 0,
        },
    }
