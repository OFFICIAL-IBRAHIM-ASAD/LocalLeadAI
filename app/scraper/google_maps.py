from urllib.parse import quote

from playwright.sync_api import sync_playwright

from app.config.settings import (
    GOOGLE_MAPS_URL,
    HEADLESS,
    PAGE_TIMEOUT,
    SLOW_MO,
    WAIT_AFTER_SEARCH,
    WAIT_AFTER_SCROLL,
    MAX_SCROLLS,
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

    def scroll_results(self):

        info("Locating results panel...")

        results_panel = self.page.locator('div[role="feed"]')

        results_panel.wait_for(timeout=30000)

        previous_count = 0

        for i in range(MAX_SCROLLS):

            results_panel.evaluate(
                "(element) => element.scrollBy(0, element.scrollHeight)"
            )

            self.page.wait_for_timeout(WAIT_AFTER_SCROLL)

            businesses = self.page.locator('a[href*="/place/"]')

            current_count = businesses.count()

            info(f"Scroll {i + 1}: {current_count} businesses loaded")

            if current_count == previous_count:
                success("No new businesses found. Stopping scroll.")
                break

            previous_count = current_count

        success("Scrolling finished.")

    def close(self):

        self.browser.close()

        self.playwright.stop()


if __name__ == "__main__":

    scraper = GoogleMapsScraper()

    scraper.search("Restaurants in Karachi")

    scraper.scroll_results()

    input("Press ENTER to close...")

    scraper.close()