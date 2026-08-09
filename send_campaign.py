import argparse
import random
import re
import time

from app.database.db import create_tables
from app.database.manager import DatabaseManager
from app.utils.logger import info, success
from app.whatsapp.browser import WhatsAppBrowser
from app.whatsapp.sender import send_message

# --- Category-specific value proposition lines ---

RESTAURANT_KEYWORDS = ["restaurant", "cafe", "food", "bakery", "catering", "diner"]
MEDICAL_KEYWORDS = ["dental", "dentist", "clinic", "hospital", "doctor", "medical", "surgeon"]

VALUE_LINES = {
    "restaurant": {
        "en": (
            "It also makes it easier for customers to view your menu, "
            "place online orders, and find your location and contact details."
        ),
        "ur": (
            "اس کے ذریعے کسٹمرز آسانی سے آپ کا مینیو دیکھ سکتے ہیں، آن لائن آرڈر کر "
            "سکتے ہیں، اور آپ کی لوکیشن اور رابطہ نمبر تلاش کر سکتے ہیں۔"
        ),
    },
    "medical": {
        "en": (
            "It also makes it easier for patients to book appointments, view "
            "your services, and find your location and contact details."
        ),
        "ur": (
            "اس کے ذریعے مریض آسانی سے اپائنٹمنٹ بک کر سکتے ہیں، آپ کی خدمات دیکھ "
            "سکتے ہیں، اور آپ کی لوکیشن اور رابطہ نمبر تلاش کر سکتے ہیں۔"
        ),
    },
    "generic": {
        "en": (
            "It also makes it easier for customers to view your services, "
            "location, contact details, and place inquiries."
        ),
        "ur": (
            "اس کے ذریعے لوگ آسانی سے آپ کی خدمات، لوکیشن، رابطہ نمبر دیکھ سکتے ہیں "
            "اور سوالات بھیج سکتے ہیں۔"
        ),
    },
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

MESSAGE_TEMPLATE_UR = """السلام علیکم، امید ہے آپ خیریت سے ہوں گے۔

میرا نام ابراہیم ہے، میں ایک طالب علم ہوں اور کاروباری اداروں کے لیے پروفیشنل ویب سائٹس بناتا ہوں۔ میں نے گوگل میپس پر {name} دیکھا اور محسوس کیا کہ آپ کے کاروبار کی کوئی ویب سائٹ موجود نہیں ہے۔

ایک پروفیشنل ویب سائٹ آپ کے کاروبار کو زیادہ کسٹمرز، آن لائن آرڈرز، اور نئے گاہکوں کا اعتماد حاصل کرنے میں مدد دے سکتی ہے۔ {value_line}

میں یہ خدمات پیش کرتا ہوں:
✅ صرف 3 دن میں پروفیشنل ویب سائٹ
✅ اگر آپ پہلے دیکھنا چاہیں تو صرف 1 دن میں ڈیمو ویب سائٹ
✅ مفت SEO تاکہ آپ کا کاروبار گوگل پر بہتر نظر آئے
✅ لائف ٹائم ڈیل (کوئی بار بار چارجز نہیں)
✅ میں اپنے پچھلے کام کے نمونے بھی دکھا سکتا ہوں

اگر آپ کو دلچسپی ہو تو بتائیں، میں ویب سائٹ کی قیمت بھی بتا دوں گا۔

شکریہ، اور آپ کا دن اچھا گزرے!"""


def normalize_phone(raw_phone: str) -> str:
    """Converts "+92 336 9399938" -> "923369399938" (digits only)."""
    return re.sub(r"\D", "", raw_phone)


def detect_category_group(category: str) -> str:
    if not category:
        return "generic"

    category_lower = category.lower()

    if any(word in category_lower for word in RESTAURANT_KEYWORDS):
        return "restaurant"

    if any(word in category_lower for word in MEDICAL_KEYWORDS):
        return "medical"

    return "generic"


def build_messages(name: str, category: str) -> tuple[str, str]:
    category_text = category.lower() if category else "business"
    group = detect_category_group(category)
    value_en = VALUE_LINES[group]["en"]
    value_ur = VALUE_LINES[group]["ur"]

    english = MESSAGE_TEMPLATE_EN.format(
        name=name, category=category_text, value_line=value_en
    )
    urdu = MESSAGE_TEMPLATE_UR.format(name=name, value_line=value_ur)

    return english, urdu


def run(limit: int, dry_run: bool):
    create_tables()
    db = DatabaseManager()

    leads = db.get_uncontacted_leads()

    if limit is not None:
        leads = leads[:limit]

    info(f"Found {len(leads)} uncontacted leads.")

    if dry_run:
        info("DRY RUN - no messages will be sent.\n")
        for row in leads:
            business_id, name, category, phone = row[0], row[1], row[2], row[3]
            english, urdu = build_messages(name, category)
            print(f"=== {name} | category: {category} | group: {detect_category_group(category)} ===")
            print("--- ENGLISH ---")
            print(english)
            print("\n--- URDU ---")
            print(urdu)
            print()
        db.close()
        return

    browser = WhatsAppBrowser()

    try:
        page = browser.start()
        input("Press ENTER once WhatsApp Web has loaded...")

        sent = 0
        failed = 0

        for i, row in enumerate(leads, start=1):
            business_id, name, category, phone = row[0], row[1], row[2], row[3]
            normalized = normalize_phone(phone)
            english, urdu = build_messages(name, category)

            info(f"[{i}/{len(leads)}] Sending to {name} ({normalized})...")

            ok_en = send_message(page, normalized, english)
            time.sleep(random.uniform(5, 10))
            ok_ur = send_message(page, normalized, urdu)

            if ok_en or ok_ur:
                db.mark_contacted(business_id)
                sent += 1
            else:
                failed += 1

            if i < len(leads):
                delay = random.uniform(15, 30)
                info(f"Waiting {delay:.0f}s before next business...")
                time.sleep(delay)

        success(f"Campaign complete: {sent} contacted, {failed} failed.")

    finally:
        browser.close()
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Send WhatsApp outreach (EN + UR) to leads without a website."
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Only message the first N leads."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview messages without sending anything."
    )

    args = parser.parse_args()
    run(limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
