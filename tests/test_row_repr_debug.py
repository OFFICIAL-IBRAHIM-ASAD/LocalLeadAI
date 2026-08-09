from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator
from app.scraper.scroller import GoogleMapsScroller

TARGETS = ["jashan", "ginsoy", "vip usmania"]


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

        found = 0

        for i in range(count):
            link = result_links.nth(i)
            name = link.get_attribute("aria-label") or link.inner_text()

            if not any(t in name.lower() for t in TARGETS):
                continue

            found += 1

            print("=" * 70)
            print(f"MATCH (index {i}): {name!r}")
            print("=" * 70)

            card = link.locator(
                'xpath=ancestor::div[@role="article"]'
            ).first

            rows = card.locator(".W4Efsd")
            row_count = rows.count()
            print(f"Row count: {row_count}\n")

            for j in range(row_count):
                row = rows.nth(j)
                text = row.inner_text()
                print(f"Row {j}: repr(text) = {text!r}")
                print(f"        '·' in text: {'·' in text}")
                if "·" in text:
                    print(f"        split('·') = {text.split(chr(183))!r}")
                print()

        print(f"\nTotal matches found: {found}")
        input("\nPress ENTER to close...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()