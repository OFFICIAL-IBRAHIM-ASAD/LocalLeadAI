from pathlib import Path

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

        # Save the current Google Maps page HTML.
        output_path = Path("output/google_maps_dom.html")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(
            page.content(),
            encoding="utf-8"
        )

        print(f"DOM saved to: {output_path}")

        input("\nDOM inspection complete. Press ENTER to close...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
