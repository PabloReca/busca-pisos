from fastapi import APIRouter, BackgroundTasks

from app.services.scraper import refresh_all_listings

router = APIRouter(prefix="/api", tags=["scraper"])


@router.post("/refresh")
def refresh_listings():
    """Update listings from Wallapop (synchronous)"""
    result = refresh_all_listings()
    return result


@router.post("/refresh/async")
def refresh_listings_async(background_tasks: BackgroundTasks):
    """Update listings from Wallapop in background"""
    background_tasks.add_task(refresh_all_listings)
    return {"message": "Refresh started in background"}
