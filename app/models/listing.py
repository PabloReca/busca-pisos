import enum
import hashlib
import json
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY

from app.db import Base


class PropertyType(enum.Enum):
    apartment = "apartment"
    house = "house"


class Listing(Base):
    __tablename__ = "listings"

    web_slug = Column(String, primary_key=True)
    property_type = Column(Enum(PropertyType), nullable=False)
    hash = Column(String(64), nullable=False)

    # Basic data
    title = Column(String)
    description = Column(Text)
    price = Column(Float)

    # Images
    images = Column(ARRAY(String))

    # Status
    reserved = Column(Boolean, default=False)

    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    postal_code = Column(String)
    city = Column(String)
    region = Column(String)
    country_code = Column(String(2))

    # Attributes
    operation = Column(String)
    surface = Column(Float)
    rooms = Column(Integer)
    bathrooms = Column(Integer)

    # Dates
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    @staticmethod
    def compute_hash(item: dict) -> str:
        """Compute SHA256 hash of item to detect changes"""
        serialized = json.dumps(item, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    @classmethod
    def from_dict(cls, item: dict, property_type: str) -> "Listing":
        """Create a Listing from a dictionary"""
        location = item.get("location", {})
        type_attrs = item.get("type_attributes", {})
        reserved = item.get("reserved", {})

        created_at = None
        modified_at = None
        if item.get("created_at"):
            try:
                created_at = datetime.fromisoformat(item["created_at"])
            except (ValueError, TypeError):
                pass
        if item.get("modified_at"):
            try:
                modified_at = datetime.fromisoformat(item["modified_at"])
            except (ValueError, TypeError):
                pass

        return cls(
            web_slug=item.get("web_slug"),
            property_type=PropertyType(property_type),
            hash=cls.compute_hash(item),
            title=item.get("title"),
            description=item.get("description"),
            price=item.get("price"),
            images=item.get("images", []),
            reserved=reserved.get("flag", False),
            latitude=location.get("latitude"),
            longitude=location.get("longitude"),
            postal_code=location.get("postal_code"),
            city=location.get("city"),
            region=location.get("region"),
            country_code=location.get("country_code"),
            operation=type_attrs.get("operation"),
            surface=type_attrs.get("surface"),
            rooms=type_attrs.get("rooms"),
            bathrooms=type_attrs.get("bathrooms"),
            created_at=created_at,
            modified_at=modified_at,
        )
