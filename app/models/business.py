from dataclasses import dataclass
from typing import Optional


@dataclass
class Business:
    """Represents a local business collected by LocalLeadAI."""

    name: str
    category: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    address: Optional[str] = None
    maps_url: Optional[str] = None

    def has_website(self) -> bool:
        """Return True if the business has a website."""
        return bool(self.website)

    def has_phone(self) -> bool:
        """Return True if the business has a phone number."""
        return bool(self.phone)

    def is_high_rated(self, minimum_rating: float = 4.0) -> bool:
        """Return True if the business meets the minimum rating."""
        return (
            self.rating is not None
            and self.rating >= minimum_rating
        )