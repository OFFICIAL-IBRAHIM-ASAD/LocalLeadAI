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

        # =========================================================
        # FIRST RESULT DEBUG
        # =========================================================

        result_link = page.locator(
            'a[href*="/place/"]'
        ).first

        print("\n" + "=" * 70)
        print("FIRST RESULT DEBUG")
        print("=" * 70)

        print("\n--- LINK TEXT ---")
        print(result_link.inner_text())

        print("\n--- LINK HTML ---")
        print(
            result_link.evaluate(
                "(element) => element.outerHTML"
            )
        )

        print("\n--- PARENT HTML ---")
        print(
            result_link.locator(
                "xpath=.."
            ).evaluate(
                "(element) => element.outerHTML"
            )
        )

        print("\n" + "=" * 70)
        print("DEBUG COMPLETE")
        print("=" * 70)

        # =========================================================
        # EXTRACTOR TEST
        # =========================================================

        print()
        print("=" * 60)
        print("EXTRACTOR TEST")
        print("=" * 60)

        extractor = GoogleMapsExtractor(page)

        businesses = extractor.extract_result_cards()

        # =========================================================
        # PRINT FIRST 5 BUSINESSES
        # =========================================================

        for index, business in enumerate(
            businesses[:5],
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
            f"Total businesses: {len(businesses)}"
        )

        input(
            "\nExtraction complete. "
            "Press ENTER to close..."
        )

    finally:
        browser_manager.close()


if __name__ == "__main__":
    main()