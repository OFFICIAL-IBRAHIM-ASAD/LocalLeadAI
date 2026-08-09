import argparse

from app.database.db import create_tables
from app.database.manager import DatabaseManager
from app.scraper.detail_extractor import visit_and_extract_details
from app.scraper.extractor import GoogleMapsExtractor
from app.scraper.google_maps import GoogleMapsScraper
from app.utils.logger import info, success
from app.validation.validator import find_near_duplicate, is_valid_business


def run(query: str, limit_details: int = None) -> None:
    """Runs the full LocalLeadAI pipeline for a single search query:

        Google Maps search
                ↓
        Scroll through results
                ↓
        Extract business data (name, category, address, rating)
                ↓
        Visit each business's own page for phone/website
                ↓
        Validate + check near-duplicates
                ↓
        Save to SQLite
    """

    create_tables()

    scraper = GoogleMapsScraper()
    db = DatabaseManager()

    try:
        scraper.start()
        scraper.search(query)

        total_loaded = scraper.scroll_results()
        info(f"Loaded {total_loaded} businesses. Extracting...")

        extractor = GoogleMapsExtractor(scraper.page)
        businesses = extractor.extract_result_cards()

        # --- Phone / website: one page visit per business ---
        to_visit = businesses
        if limit_details is not None:
            to_visit = businesses[:limit_details]
            info(
                f"--limit set: only fetching phone/website for "
                f"first {limit_details} of {len(businesses)} businesses."
            )

        info(f"Visiting {len(to_visit)} business pages for phone/website...")

        for i, business in enumerate(to_visit, start=1):
            if not business.maps_url:
                continue

            phone, website = visit_and_extract_details(
                scraper.page, business.maps_url
            )
            business.phone = phone
            business.website = website

            info(
                f"[{i}/{len(to_visit)}] {business.name}: "
                f"phone={phone!r}, website={website!r}"
            )

        # --- Validate + save ---
        existing_rows = db.get_all_businesses()
        # columns: id, name, category, phone, website, rating,
        #          reviews, address, maps_url, ...
        known = [(row[1], row[7]) for row in existing_rows]

        saved = 0
        skipped_invalid = 0
        skipped_duplicate = 0
        skipped_existing = 0

        for business in businesses:
            valid, reason = is_valid_business(business)
            if not valid:
                skipped_invalid += 1
                info(f"Skipped (invalid: {reason}): {business.name!r}")
                continue

            duplicate_of = find_near_duplicate(
                business.name, business.address, known
            )
            if duplicate_of:
                skipped_duplicate += 1
                info(
                    f"Skipped (near-duplicate of {duplicate_of!r}): "
                    f"{business.name!r}"
                )
                continue

            inserted = db.add_business(
                name=business.name,
                category=business.category,
                phone=business.phone,
                website=business.website,
                rating=business.rating,
                reviews=business.reviews,
                address=business.address,
                maps_url=business.maps_url,
            )

            if inserted:
                saved += 1
                known.append((business.name, business.address))
            else:
                skipped_existing += 1

        success(
            f"Saved {saved} new businesses. "
            f"Skipped: {skipped_invalid} invalid, "
            f"{skipped_duplicate} near-duplicates, "
            f"{skipped_existing} already in database."
        )

    finally:
        db.close()
        scraper.close()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Search Google Maps for local businesses and "
            "save them as leads in the database."
        )
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="Restaurants in Karachi",
        help=(
            "Google Maps search query, e.g. "
            "'Restaurants in Karachi'. Defaults to that if omitted."
        ),
    )
    parser.add_argument(
        "--limit-details",
        type=int,
        default=None,
        help=(
            "Only fetch phone/website for the first N businesses "
            "(for quick testing). Default: all businesses."
        ),
    )

    args = parser.parse_args()
    run(args.query, limit_details=args.limit_details)


if __name__ == "__main__":
    main()