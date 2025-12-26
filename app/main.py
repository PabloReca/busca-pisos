from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import STATICS_DIR
from app.routers import health, listings, scraper

app = FastAPI(title="BuscaPisos")

# Brotli compression (quality 6)
app.add_middleware(BrotliMiddleware, quality=6, minimum_size=500)

# Routers
app.include_router(health.router)
app.include_router(listings.router)
app.include_router(scraper.router)

# Serve static files
app.mount("/static", StaticFiles(directory=str(STATICS_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATICS_DIR / "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
