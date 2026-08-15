import argparse
import random
import re
import time

from app.database.db import create_tables
from app.database.manager import DatabaseManager
from app.utils.logger import info, success
from app.whatsapp.browser import WhatsAppBrowser
from app.whatsapp.sender import send_message

RESTAURANT_KEYWORDS = ["restaurant", "cafe", "food", "bakery", "catering", "diner"]
MEDICAL_KEYWORDS = ["dental", "dentist", "clinic", "hospital", "doctor", "medical", "surgeon"]

VALUE_LINES = {
    "restaurant": (
        "It also makes it easier for customers to view your menu, "
        "place online orders, and find your location and contact details."
    ),
    "medical": (
        "It also makes it easier for patients to book appointments, view "
        "your services, and find your location and contact details."
    ),
    "generic": (
        "It also makes it easier for customers to view your services, "
        "location, contact details, and place inquiries."
    ),
}

MESSAGE_TEMPLATE_EN = """Hi, I hope you're doing well.

I'm Ibrahim, a student who designs professional websites for businesses. I came across {name} on Google Maps and noticed your {category} doesn't have a dedicated website yet.

A professional website can help your business receive more customer visits, online orders, and build greater trust with new customers. {value_line}

Here's what I offer:
✅ Professional website delivered in 3 days
✅ Mock/demo website in just 1 day if you'd like to see a preview first
✅ Free SEO to help your business appear better on Google
✅ Lifetime deal (no recurring website development charges)
✅ I can also share samples of my previous work if you'd like

If you're interested, just let me know and I'll share the cost of the website.

Thank you, and have a great day!"""


def normalize_phone(raw_phone: str) -> str:
    return re.sub(r"\D", "", raw_phone)


def is_mobile_number(normalized_phone: str) -> bool:
    return normalized_phone.startswith("923") and len(normalized_phone) == 12


def detect_category_group(category: str) -> str:
    if not category:
        return "generic"
    category_lower = category.lower()
    if any(word in category_lower for word in RESTAURANT_KEYWORDS):
        return "restaurant"
    if any(word in category_lower for word in MEDICAL_KEYWORDS):
        return "medical"
    return "generic"


def build_message(name: str, category: str) -> str:
    category_text = category.lower() if category else "business"
    group = detect_category_group(category)
    value_line = VALUE_LINES[group]
    return MESSAGE_TEMPLATE_EN.format(
        name=name, category=category_text, value_line=value_line
    )


def get_campaign_leads(limit: int = None):
    """Fetches uncontacted leads with mobile numbers, split from
    landlines. Returns (mobile_leads, landline_leads).

    Already excludes businesses previously marked whatsapp_failed
    (see DatabaseManager.get_uncontacted_leads)."""
    db = DatabaseManager()
    leads = db.get_uncontacted_leads()
    db.close()

    mobile_leads = []
    landline_leads = []

    for row in leads:
        phone = row[3]
        normalized = normalize_phone(phone)
        if is_mobile_number(normalized):
            mobile_leads.append(row)
        else:
            landline_leads.append(row)

    if limit is not None:
        mobile_leads = mobile_leads[:limit]

    return mobile_leads, landline_leads


def send_to_leads(page, leads, progress_callback=None):
    """Sends one English message per lead. Failed sends are
    marked whatsapp_failed so they don't get retried - they'll
    show up in the cold-call export instead.

    Returns:
        (sent_count, failed_count)
    """
    db = DatabaseManager()
    sent = 0
    failed = 0

    for i, row in enumerate(leads, start=1):
        business_id, name, category, phone = row[0], row[1], row[2], row[3]
        normalized = normalize_phone(phone)
        message = build_message(name, category)

        info(f"[{i}/{len(leads)}] Sending to {name} ({normalized})...")

        ok = send_message(page, normalized, message)

        if ok:
            db.mark_contacted(business_id)
            sent += 1
        else:
            db.mark_whatsapp_failed(business_id)
            failed += 1

        if progress_callback:
            progress_callback(i, len(leads), name, ok)

        if i < len(leads):
            delay = random.uniform(20, 40)
            info(f"Waiting {delay:.0f}s before next business...")
            time.sleep(delay)

    db.close()
    return sent, failed


def run(limit: int, dry_run: bool, account: str = "main"):
    create_tables()

    mobile_leads, landline_leads = get_campaign_leads(limit)

    if landline_leads:
        info(
            f"{len(landline_leads)} leads have landline numbers "
            f"(no WhatsApp possible) - skipped, not attempted:"
        )
        for row in landline_leads:
            info(f"  - {row[1]} ({row[3]})")

    info(f"Found {len(mobile_leads)} mobile leads to message.")

    if dry_run:
        info("DRY RUN - no messages will be sent.\n")
        for row in mobile_leads:
            business_id, name, category, phone = row[0], row[1], row[2], row[3]
            message = build_message(name, category)
            print(f"=== {name} | category: {category} | group: {detect_category_group(category)} ===")
            print(message)
            print()
        return

    info(f"Using WhatsApp account/session: {account!r}")
    browser = WhatsAppBrowser(account=account)

    try:
        page = browser.start()
        input("Press ENTER once WhatsApp Web has loaded...")

        sent, failed = send_to_leads(page, mobile_leads)
        success(f"Campaign complete: {sent} contacted, {failed} failed.")

    finally:
        browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Send WhatsApp outreach (English only) to leads without a website."
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--account", type=str, default="main")

    args = parser.parse_args()
    run(limit=args.limit, dry_run=args.dry_run, account=args.account)


if __name__ == "__main__":
    main()
