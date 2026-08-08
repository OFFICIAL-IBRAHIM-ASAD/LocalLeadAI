from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator
from app.scraper.scroller import GoogleMapsScroller


class GoogleMapsScraper:
    """Coordinates the Google Maps scraping workflow."""

    def __init__(self):
        self.browser = BrowserManager()
        self.page = None
        self.navigator = None
        self.scroller = None

    def start(self):
        """Start the browser and initialize scraper components."""

        self.page = self.browser.start()

        self.navigator = GoogleMapsNavigator(self.page)
        self.scroller = GoogleMapsScroller(self.page)

    def search(self, query: str):
        """Search Google Maps for a query."""

        if self.navigator is None:
            raise RuntimeError(
                "Scraper has not been started. Call start() first."
            )

        return self.navigator.search(query)

    def scroll_results(self) -> int:
        """Scroll through Google Maps results."""

        if self.scroller is None:
            raise RuntimeError(
                "Scraper has not been started. Call start() first."
            )

        return self.scroller.scroll()

    def close(self):
        """Close the scraper and browser."""

        self.browser.close()


if __name__ == "__main__":

    scraper = GoogleMapsScraper()

    try:
        scraper.start()

        scraper.search("Restaurants in Karachi")

        total = scraper.scroll_results()

        print(f"Final businesses loaded: {total}")

        input("Press ENTER to close...")

    finally:
        scraper.close()