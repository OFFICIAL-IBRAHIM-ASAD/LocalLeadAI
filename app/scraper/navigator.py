from urllib.parse import quote

from playwright.sync_api import Page

from app.config.settings import (
    GOOGLE_MAPS_URL,
    WAIT_AFTER_SEARCH,
)
from app.utils.logger import info, success


class GoogleMapsNavigator:
    """Handles navigation and searching on Google Maps."""

    def __init__(self, page: Page):
        self.page = page

    def search(self, query: str):
        """Search Google Maps for the given query."""

        encoded_query = quote(query)

        url = f"{GOOGLE_MAPS_URL}/search/{encoded_query}"

        info(f"Opening: {url}")

        self.page.goto(
            url,
            wait_until="domcontentloaded"
        )

        self.page.wait_for_timeout(WAIT_AFTER_SEARCH)

        success(f"Search completed: {query}")

        return self.page
