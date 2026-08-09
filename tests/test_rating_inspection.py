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

        count = result_links.count()

        print(f"\nTotal results: {count}")

        for index in range(min(count, 10)):

            link = result_links.nth(index)

            print(f"\n===== BUSINESS {index + 1} =====")
            print(f"Name: {link.inner_text().strip()}")

            # Print the parent/card text so we can inspect
            # rating and review information.
            card = link.locator("xpath=..")

            print("Parent text:")
            print(card.inner_text())

        input("\nRating inspection complete. Press ENTER to close...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
