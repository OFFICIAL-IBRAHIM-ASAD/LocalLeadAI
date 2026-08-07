from urllib.parse import quote

from playwright.sync_api import sync_playwright

from app.config.settings import (
    GOOGLE_MAPS_URL,
    HEADLESS,
    PAGE_TIMEOUT,
    SLOW_MO,
    WAIT_AFTER_SEARCH,
)
from app.utils.logger import info, success


class GoogleMapsScraper:

    def __init__(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO
        )

        self.page = self.browser.new_page()

        self.page.set_default_timeout(PAGE_TIMEOUT)

    def search(self, query: str):

        encoded = quote(query)

        url = f"{GOOGLE_MAPS_URL}/search/{encoded}"

        info(f"Opening: {url}")

        self.page.goto(
            url,
            wait_until="domcontentloaded"
        )

        self.page.wait_for_timeout(WAIT_AFTER_SEARCH)

        success("Search completed.")

    def close(self):

        self.browser.close()

        self.playwright.stop()


if __name__ == "__main__":

    scraper = GoogleMapsScraper()

    scraper.search("Restaurants in Karachi")

    input("Press ENTER to close...")

    scraper.close()