from pathlib import Path

from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator


def main():
    browser = BrowserManager()

    try:
        page = browser.start()

        navigator = GoogleMapsNavigator(page)
        navigator.search("KFC Karachi")

        result_links = page.locator('a[href*="/place/"]')
        first_link = result_links.first
        url = first_link.get_attribute("href")
        name = first_link.get_attribute("aria-label")

        print(f"Testing against: {name}")
        print(f"URL: {url}\n")

        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        phone_buttons = page.locator('button[data-item-id^="phone"]')
        print(f"Phone button count: {phone_buttons.count()}")
        if phone_buttons.count() > 0:
            print(phone_buttons.first.evaluate("el => el.outerHTML"))

        website_links = page.locator('a[data-item-id="authority"]')
        print(f"\nWebsite link count: {website_links.count()}")
        if website_links.count() > 0:
            print(website_links.first.evaluate("el => el.outerHTML"))

        output_path = Path("output/detail_page_dom.html")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(page.content(), encoding="utf-8")
        print(f"\nFull page saved to: {output_path}")

        input("\nPress ENTER to close...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
