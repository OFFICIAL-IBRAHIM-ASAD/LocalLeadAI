from playwright.sync_api import Browser, Page, Playwright, sync_playwright

from app.config.settings import HEADLESS, PAGE_TIMEOUT, SLOW_MO
from app.utils.logger import info, success


class BrowserManager:
    """Manages the Playwright browser lifecycle."""

    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.page: Page | None = None

    def start(self) -> Page:
        """Start Playwright and return a configured browser page."""

        info("Starting browser...")

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO
        )

        self.page = self.browser.new_page()

        self.page.set_default_timeout(PAGE_TIMEOUT)

        success("Browser started.")

        return self.page

    def close(self):
        """Close the browser and Playwright."""

        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

        self.page = None

        success("Browser closed.")
