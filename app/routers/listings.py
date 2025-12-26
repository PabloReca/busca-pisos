from typing import Optional

from fastapi import APIRouter, Query

from app.services.listings import (
    filter_listings,
    get_stats,
    load_listings,
    sort_listings,
)

router = APIRouter(prefix="/api", tags=["listings"])


@router.get("/listings")
def get_listings(
    property_type: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    min_rooms: Optional[int] = Query(None),
    max_rooms: Optional[int] = Query(None),
    min_bathrooms: Optional[int] = Query(None),
    max_bathrooms: Optional[int] = Query(None),
    max_distance: Optional[float] = Query(None),
    sort_by: str = Query("price"),
    sort_order: str = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get listings with filters and pagination"""
    listings = load_listings()

    listings = filter_listings(
        listings,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        min_rooms=min_rooms,
        max_rooms=max_rooms,
        min_bathrooms=min_bathrooms,
        max_bathrooms=max_bathrooms,
        max_distance=max_distance,
    )

    listings = sort_listings(listings, sort_by=sort_by, sort_order=sort_order)

    # Pagination
    total = len(listings)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = listings[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "listings": paginated,
    }


@router.get("/stats")
def get_listings_stats():
    """General statistics"""
    listings = load_listings()
    return get_stats(listings)
