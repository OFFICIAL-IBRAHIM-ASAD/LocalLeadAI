from app.whatsapp.browser import WhatsAppBrowser

# Put YOUR OWN phone number here for this test, with country
# code, digits only (no +, no spaces). Example: 923001234567
TEST_PHONE = "923020420874"
TEST_MESSAGE = "Test message from LocalLeadAI"


def main():
    browser = WhatsAppBrowser()

    try:
        page = browser.start()

        url = f"https://web.whatsapp.com/send?phone={TEST_PHONE}&text={TEST_MESSAGE}"
        page.goto(url, timeout=60000)

        print("Waiting for chat to load...")
        page.wait_for_timeout(5000)

        # Try to find the send button several plausible ways.
        candidates = [
            'button[aria-label="Send"]',
            'span[data-icon="send"]',
            'span[data-icon="wds-ic-send-filled"]',
        ]

        for selector in candidates:
            el = page.locator(selector)
            print(f"{selector}: count={el.count()}")

        print("\nDo NOT click send yet — just checking selectors.")
        input("Press ENTER to close...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
