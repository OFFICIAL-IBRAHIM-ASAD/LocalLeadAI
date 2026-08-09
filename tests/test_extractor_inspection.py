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
        total = scroller.scroll()

        print(f"\nTotal businesses loaded: {total}")

        businesses = page.locator('a[href*="/place/"]')

        count = businesses.count()

        print(f"Business links found by selector: {count}")

        for i in range(min(count, 10)):
            element = businesses.nth(i)

            print(f"\n--- Business {i + 1} ---")
            print("Text:", element.inner_text())
            print("Href:", element.get_attribute("href"))

        input("\nInspection complete. Press ENTER to close...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
