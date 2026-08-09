from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator
from app.scraper.scroller import GoogleMapsScroller
from app.scraper.extractor import GoogleMapsExtractor


def main():

    browser = BrowserManager()

    try:
        page = browser.start()

        navigator = GoogleMapsNavigator(page)
        navigator.search("Restaurants in Karachi")

        scroller = GoogleMapsScroller(page)
        total = scroller.scroll()

        print(f"\nBusinesses loaded: {total}")

        extractor = GoogleMapsExtractor(page)
        businesses = extractor.extract_result_cards()

        print("\n===== EXTRACTED BUSINESSES =====")

        for index, business in enumerate(businesses[:10], start=1):

            print(f"\n{index}. {business.name}")
            print(f"   Rating: {business.rating}")
            print(f"   Maps URL: {business.maps_url}")

        print(
            f"\nTotal Business objects created: "
            f"{len(businesses)}"
        )

        input("\nExtraction complete. Press ENTER to close...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
