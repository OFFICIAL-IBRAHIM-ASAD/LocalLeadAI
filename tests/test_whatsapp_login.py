from app.whatsapp.browser import WhatsAppBrowser


def main():
    browser = WhatsAppBrowser()

    try:
        page = browser.start()

        print("If this is your first time: scan the QR code shown in the browser.")
        print("If you've logged in before: it should load straight into WhatsApp.")

        input("\nPress ENTER once WhatsApp Web has loaded (chats visible)...")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
