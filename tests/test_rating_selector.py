from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator
from app.scraper.scroller import GoogleMapsScroller


def main():

    browser = BrowserManager()

    try:
        page = browser.start()

        navigator = GoogleMapsNavigator(page)
        navigator.search("Restaurants in Karachi")

        scroller = GoogleMapsScroller(page)
        scroller.scroll()

        result_links = page.locator('a[href*="/place/"]')

        print(f"\nTotal results: {result_links.count()}")

        for index in range(min(result_links.count(), 3)):

            link = result_links.nth(index)

            print(f"\n{'=' * 60}")
            print(f"BUSINESS {index + 1}")
            print(f"Name: {link.inner_text().strip()}")

            # Get the business card.
            card = link.locator("xpath=..")

            # Find elements containing a decimal number such as 4.1
            rating_candidates = card.locator(
                '[aria-label*="star"], [aria-label*="rating"]'
            )

            print(f"Rating candidates: {rating_candidates.count()}")

            for i in range(rating_candidates.count()):

                element = rating_candidates.nth(i)

                try:
                    print(
                        f"Candidate {i + 1}: "
                        f"text={element.inner_text()!r}, "
                        f"aria-label={element.get_attribute('aria-label')!r}"
                    )
                except Exception:
                    pass

        input("\nInspection complete. Press ENTER to close...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
