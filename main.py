import argparse

from app.database.db import create_tables
from app.database.manager import DatabaseManager
from app.scraper.extractor import GoogleMapsExtractor
from app.scraper.google_maps import GoogleMapsScraper
from app.utils.logger import info, success


def run(query: str) -> None:
    """Runs the full LocalLeadAI pipeline for a single search query:

        Google Maps search
                ↓
        Scroll through results
                ↓
        Extract business data
                ↓
        Save to SQLite (skipping duplicates by maps_url)
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

        saved = 0
        skipped = 0

        for business in businesses:
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
            else:
                skipped += 1

        success(
            f"Saved {saved} new businesses "
            f"({skipped} already in database)."
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

    args = parser.parse_args()
    run(args.query)


if __name__ == "__main__":
    main()