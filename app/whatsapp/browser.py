from pathlib import Path

from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "whatsapp_session"


class WhatsAppBrowser:
    """Manages a persistent WhatsApp Web browser session, so you
    only scan the QR code once."""

    def __init__(self):
        self.playwright = None
        self.context = None
        self.page = None

    def start(self):
        SESSION_DIR.mkdir(parents=True, exist_ok=True)

        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            str(SESSION_DIR),
            headless=False,
        )

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

        self.page.goto("https://web.whatsapp.com", timeout=60000)

        return self.page

    def close(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
