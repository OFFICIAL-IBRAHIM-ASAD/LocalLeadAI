from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator
from app.scraper.scroller import GoogleMapsScroller
from app.scraper.extractor import GoogleMapsExtractor


def main():

    browser_manager = BrowserManager()
    page = browser_manager.start()

    try:
        navigator = GoogleMapsNavigator(page)

        navigator.search(
            "Restaurants in Karachi"
        )

        scroller = GoogleMapsScroller(page)
        scroller.scroll()

        extractor = GoogleMapsExtractor(page)

        businesses = extractor.extract_result_cards()

        print()
        print("=" * 60)
        print("EXTRACTED BUSINESS DETAILS")
        print("=" * 60)

        for index, business in enumerate(
            businesses[:10],
            start=1
        ):
            print()
            print(f"BUSINESS {index}")
            print(f"Name: {business.name}")
            print(f"Rating: {business.rating}")
            print(f"Category: {business.category}")
            print(f"Address: {business.address}")
            print(f"Maps URL: {business.maps_url}")

        print()
        print(
            f"Total Business objects created: "
            f"{len(businesses)}"
        )

        input(
            "\nExtraction complete. "
            "Press ENTER to close..."
        )

    finally:
        browser_manager.close()


if __name__ == "__main__":
    main()