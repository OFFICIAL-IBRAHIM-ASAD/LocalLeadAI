import re
from typing import Optional, Tuple

from playwright.sync_api import Page

from app.utils.logger import info


def extract_phone_and_website(page: Page) -> Tuple[Optional[str], Optional[str]]:
    """Extracts phone number and website from an already-opened
    Google Maps business detail page.

    Returns:
        (phone, website) - either may be None if not listed.
    """
    phone = _extract_phone(page)
    website = _extract_website(page)
    return phone, website


def _extract_phone(page: Page) -> Optional[str]:
    button = page.locator('button[data-item-id^="phone"]').first

    if button.count() == 0:
        return None

    aria_label = button.get_attribute("aria-label")
    if not aria_label:
        return None

    # aria-label looks like "Phone: +92 308 9369368 "
    match = re.search(r"Phone:\s*(.+)", aria_label)
    if not match:
        return None

    return match.group(1).strip()


def _extract_website(page: Page) -> Optional[str]:
    link = page.locator('a[data-item-id="authority"]').first

    if link.count() == 0:
        return None

    href = link.get_attribute("href")
    return href.strip() if href else None


def visit_and_extract_details(page: Page, maps_url: str) -> Tuple[Optional[str], Optional[str]]:
    """Navigates to a business's own Maps page and extracts
    phone/website. Caller is responsible for navigating back to
    the results list afterward if needed."""
    try:
        page.goto(maps_url, timeout=30000)
        page.wait_for_timeout(2000)
        return extract_phone_and_website(page)
    except Exception as error:
        info(f"Could not load detail page: {error}")
        return None, None
