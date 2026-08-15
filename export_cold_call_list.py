import csv
import re
from pathlib import Path

from app.database.db import create_tables
from app.database.manager import DatabaseManager
from app.utils.logger import info, success


def normalize_phone(raw_phone: str) -> str:
    return re.sub(r"\D", "", raw_phone)


def is_mobile_number(normalized_phone: str) -> bool:
    return normalized_phone.startswith("923") and len(normalized_phone) == 12


def main():
    create_tables()
    db = DatabaseManager()

    all_rows = db.get_businesses_without_websites()
    failed_rows = db.get_whatsapp_failed_leads()
    db.close()

    failed_ids = {row[0] for row in failed_rows}

    cold_call_leads = []

    for row in all_rows:
        business_id, name, category, phone, address = row[0], row[1], row[2], row[3], row[7]

        if not phone or not phone.strip():
            continue

        if business_id in failed_ids:
            reason = "whatsapp_failed"
        else:
            normalized = normalize_phone(phone)
            if is_mobile_number(normalized):
                continue  # goes through WhatsApp instead
            reason = "landline"

        cold_call_leads.append({
            "name": name,
            "category": category or "",
            "phone": phone,
            "address": address or "",
            "reason": reason,
        })

    info(f"Found {len(cold_call_leads)} leads for cold calling.")

    output_path = Path("output/cold_call_list.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "category", "phone", "address", "reason"])
        writer.writeheader()
        writer.writerows(cold_call_leads)

    success(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
