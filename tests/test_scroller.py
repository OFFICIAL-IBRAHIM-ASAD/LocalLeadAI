from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator
from app.scraper.scroller import GoogleMapsScroller


def main():

    browser = BrowserManager()
    page = browser.start()

    navigator = GoogleMapsNavigator(page)
    navigator.search("Restaurants in Karachi")

    scroller = GoogleMapsScroller(page)
    total = scroller.scroll()

    print(f"Final businesses loaded: {total}")

    input("Scrolling completed. Press ENTER to close...")

    browser.close()


if __name__ == "__main__":
    main()
