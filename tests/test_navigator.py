from app.scraper.browser import BrowserManager
from app.scraper.navigator import GoogleMapsNavigator


def main():

    browser = BrowserManager()
    page = browser.start()

    navigator = GoogleMapsNavigator(page)

    navigator.search("Restaurants in Karachi")

    input("Google Maps search completed. Press ENTER to close...")

    browser.close()


if __name__ == "__main__":
    main()
