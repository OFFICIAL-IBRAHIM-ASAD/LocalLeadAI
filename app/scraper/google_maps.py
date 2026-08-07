from playwright.sync_api import sync_playwright


class GoogleMapsScraper:

    def __init__(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False,
            slow_mo=300
        )

        self.page = self.browser.new_page()

    def search(self, query):

        print(f"Searching for: {query}")

        self.page.goto(
                       "https://www.google.com/maps",
                        wait_until="domcontentloaded",
                        timeout=60000
)

        self.page.locator('input[id="searchboxinput"]').wait_for(timeout=30000)

        search_box = self.page.locator('input[id="searchboxinput"]')

        search_box.fill(query)

        self.page.keyboard.press("Enter")

        self.page.wait_for_timeout(7000)

    def close(self):
        self.browser.close()
        self.playwright.stop()


if __name__ == "__main__":

    scraper = GoogleMapsScraper()

    scraper.search("Restaurants in Karachi")

    input("Press ENTER to close...")

    scraper.close()