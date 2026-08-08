from app.scraper.browser import BrowserManager


def main():

    browser = BrowserManager()

    page = browser.start()

    page.goto("https://www.google.com")

    input("Google opened. Press ENTER to close...")

    browser.close()


if __name__ == "__main__":
    main()
