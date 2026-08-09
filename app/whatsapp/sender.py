import random
import time
import urllib.parse

from app.utils.logger import info, success


def send_message(page, phone: str, message: str) -> bool:
    """Sends a WhatsApp message to a phone number.

    Args:
        page: an already-logged-in WhatsApp Web page
              (from WhatsAppBrowser.start()).
        phone: digits only, with country code, e.g. "923001234567".
        message: the text to send.

    Returns:
        True if sent, False if it failed.
    """
    encoded_message = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"

    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        send_button = page.locator('button[aria-label="Send"]')

        if send_button.count() == 0:
            info(f"Could not find send button for {phone} (invalid number?)")
            return False

        send_button.first.click()
        page.wait_for_timeout(2000)

        success(f"Message sent to {phone}")
        return True

    except Exception as error:
        info(f"Failed to send to {phone}: {error}")
        return False


def send_bulk(page, contacts, message_template, min_delay=15, max_delay=30):
    """Sends messages to multiple contacts with a random delay
    between each, to reduce ban risk.

    Args:
        contacts: list of (phone, name) tuples.
        message_template: string, can use {name} placeholder.
        min_delay / max_delay: seconds to wait between sends.
    """
    sent = 0
    failed = 0

    for i, (phone, name) in enumerate(contacts, start=1):
        message = message_template.format(name=name)

        info(f"[{i}/{len(contacts)}] Sending to {name} ({phone})...")

        if send_message(page, phone, message):
            sent += 1
        else:
            failed += 1

        if i < len(contacts):
            delay = random.uniform(min_delay, max_delay)
            info(f"Waiting {delay:.0f}s before next message...")
            time.sleep(delay)

    success(f"Bulk send complete: {sent} sent, {failed} failed.")
