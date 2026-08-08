from playwright.sync_api import Locator, Page

from app.config.settings import (
    MAX_SCROLLS,
    WAIT_AFTER_SCROLL,
)
from app.utils.logger import info, success


class GoogleMapsScroller:
    """Handles scrolling through Google Maps search results."""

    def __init__(self, page: Page):
        self.page = page

    def _get_results_panel(self) -> Locator:
        """Locate the Google Maps results panel."""

        info("Locating results panel...")

        results_panel = self.page.locator('div[role="feed"]')

        results_panel.wait_for(timeout=30000)

        return results_panel

    def scroll(self) -> int:
        """
        Scroll through Google Maps results.

        Returns:
            int: Number of business result links currently loaded.
        """

        results_panel = self._get_results_panel()

        previous_count = 0

        for scroll_number in range(1, MAX_SCROLLS + 1):

            results_panel.evaluate(
                "(element) => element.scrollBy(0, element.scrollHeight)"
            )

            self.page.wait_for_timeout(WAIT_AFTER_SCROLL)

            businesses = self.page.locator('a[href*="/place/"]')

            current_count = businesses.count()

            info(
                f"Scroll {scroll_number}: "
                f"{current_count} businesses loaded"
            )

            if current_count == previous_count:
                success("No new businesses found. Stopping scroll.")
                break

            previous_count = current_count

        success("Scrolling finished.")

        return previous_count
