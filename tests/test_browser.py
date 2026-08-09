from app.scraper.browser import BrowserManager


def main():

    browser_manager = BrowserManager()
    page = browser_manager.start()

    try:

        print("Opening Google...")

        page.goto(
            "https://www.google.com",
            wait_until="domcontentloaded",
            timeout=30000
        )

        print("Google opened successfully.")
        print("Title:", page.title())

        input("Press ENTER to close...")

    finally:
        browser_manager.close()


if __name__ == "__main__":
    main()