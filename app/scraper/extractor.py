import re
from typing import List, Optional

from playwright.sync_api import Page

from app.models.business import Business
from app.utils.logger import info, success


# Matches any Google Maps "hours/status" phrasing, not just the
# specific wording we happened to see during debugging:
#   "Open · Closes 9 PM"
#   "Closed · Opens 9 AM"
#   "Open 24 hours"
#   "Closes soon"
#   "Temporarily closed"
#   "Permanently closed"
HOURS_KEYWORDS_PATTERN = re.compile(
    r"\b(open|closed|opens|closes|24 hours|"
    r"temporarily closed|permanently closed)\b",
    re.IGNORECASE,
)

# Matches clock-time text like "9 PM", "1:30 AM" — a second,
# independent signal that a row is describing hours rather than
# a category/address, in case the wording doesn't match the
# keyword list above. \s already matches the narrow no-break
# space (U+202F) Google uses between the number and AM/PM.
TIME_PATTERN = re.compile(r"\d{1,2}(:\d{2})?\s?(AM|PM)", re.IGNORECASE)

# Google renders small inline icons (e.g. the "wheelchair
# accessible entrance" glyph) as single characters from the
# Unicode Private Use Area rather than as normal text. These
# have no visible content but aren't whitespace either, so a
# plain .strip() won't remove them. They show up as their own
# "·"-separated segment between category and address, e.g.:
#   "Restaurant · <icon> · Near Danzoo, Precinct 19"
_PUA_RANGES = (
    (0xE000, 0xF8FF),      # BMP Private Use Area
    (0xF0000, 0xFFFFD),    # Supplementary PUA-A
    (0x100000, 0x10FFFD),  # Supplementary PUA-B
)


def _looks_like_hours(text: str) -> bool:
    """True if this row text is describing opening hours/status
    rather than a business category or address."""
    if not text:
        return False
    return bool(
        HOURS_KEYWORDS_PATTERN.search(text) or TIME_PATTERN.search(text)
    )


def _strip_icon_chars(text: str) -> str:
    """Removes Private Use Area icon glyphs, which are invisible
    when printed but aren't whitespace, so they'd otherwise slip
    past a plain .strip() and be mistaken for real content."""
    return "".join(
        ch for ch in text
        if not any(lo <= ord(ch) <= hi for lo, hi in _PUA_RANGES)
    )


def _is_meaningful(text: str) -> bool:
    """True if a "·"-separated segment has real visible content
    (i.e. isn't just whitespace and/or an icon glyph)."""
    return bool(_strip_icon_chars(text).strip())


def _looks_like_rating_or_price(first_part: str) -> bool:
    """True if a row's first segment is rating/review-count/price
    info rather than a category, e.g. "4.4(8,312)" or a price
    range row. Real Google Maps categories are always words, so
    any row whose first segment starts with a digit is something
    else — never a category/address row — and should be skipped
    entirely rather than parsed."""
    return bool(first_part) and first_part[0].isdigit()


class GoogleMapsExtractor:
    """Extracts business information from Google Maps search results."""

    def __init__(self, page: Page):
        self.page = page

    def extract_result_cards(self) -> List[Business]:
        """Extracts business information from Google Maps search results.

        Returns:
            List[Business]: A list of Business objects containing
            extracted information.
        """
        businesses = []

        result_links = self.page.locator('a[href*="/place/"]')
        count = result_links.count()

        info(f"Extracting {count} business results...")

        for index in range(count):
            link = result_links.nth(index)

            try:
                business = self._extract_single(link)
                if business is not None:
                    businesses.append(business)
            except Exception as error:
                info(f"Could not extract result {index + 1}: {error}")

        success(f"Extracted {len(businesses)} businesses.")
        return businesses

    # =====================================================
    # PER-RESULT EXTRACTION
    # =====================================================

    def _extract_single(self, link) -> Optional[Business]:
        name = link.get_attribute("aria-label")
        if not name:
            name = link.inner_text().strip()

        maps_url = link.get_attribute("href")

        if not name or not maps_url:
            return None

        card = link.locator('xpath=ancestor::div[@role="article"]').first
        if card.count() == 0:
            info(f"Could not find card for: {name}")
            return None

        rating = self._extract_rating(card)
        category, address = self._extract_category_and_address(card)

        return Business(
            name=name,
            category=category,
            address=address,
            rating=rating,
            maps_url=maps_url,
        )

    def _extract_rating(self, card) -> Optional[float]:
        rating_element = card.locator(
            '[role="img"][aria-label*="stars"]'
        ).first

        if rating_element.count() == 0:
            return None

        aria_label = rating_element.get_attribute("aria-label")
        if not aria_label:
            return None

        try:
            return float(aria_label.split(" ")[0])
        except (ValueError, IndexError):
            return None

    # =====================================================
    # CATEGORY / ADDRESS
    # =====================================================

    def _get_candidate_rows(self, card) -> List[str]:
        """Returns de-duplicated, non-empty text of every .W4Efsd
        row in the card, in DOM order. De-duping matters because
        Google sometimes nests a .W4Efsd div inside another
        .W4Efsd div, which would otherwise return the same text
        twice."""
        rows_locator = card.locator(".W4Efsd")
        row_count = rows_locator.count()

        rows = []
        seen = set()

        for row_index in range(row_count):
            text = rows_locator.nth(row_index).inner_text().strip()
            if not text or text in seen:
                continue
            seen.add(text)
            rows.append(text)

        return rows

    def _extract_category_and_address(self, card):
        """Deterministically separates category/address text from
        opening-hours text.

        Observed DOM pattern:
            "Category · Address"   <- what we want
            "Open · Closes 9 PM"   <- must be excluded, in ANY
                                       phrasing Google uses
        """
        category = None
        address = None

        rows = self._get_candidate_rows(card)

        # --- Primary: a row shaped like "Category · Address" ---
        # Google sometimes inserts invisible icon segments between
        # the two, e.g. "Category · <icon> · Address", so we filter
        # down to meaningful parts first and then take the first
        # as category and the LAST as address — not parts[1], which
        # would grab an icon segment when one is present.
        for text in rows:
            if _looks_like_hours(text):
                continue

            if "·" not in text:
                continue

            parts = [p.strip() for p in text.split("·")]
            parts = [
                p for p in parts
                if _is_meaningful(p) and not _looks_like_hours(p)
            ]

            if not parts:
                continue

            if _looks_like_rating_or_price(parts[0]):
                # This is a rating/review-count/price row (e.g.
                # "4.4(8,312) · Rs 1,000-7,000"), not category/
                # address — skip it and keep looking.
                continue

            category = parts[0]
            if len(parts) >= 2:
                address = parts[-1]
            break

        # --- Fallback: category with no "·" present at all ---
        if category is None:
            for text in rows:
                if _looks_like_hours(text):
                    continue
                if len(text) > 100:
                    continue
                category = text
                break

        # --- Fallback: address in a different row than category ---
        if address is None:
            for text in rows:
                if _looks_like_hours(text):
                    continue
                if text == category:
                    continue
                if "·" not in text:
                    continue

                parts = [p.strip() for p in text.split("·")]
                parts = [
                    p for p in parts
                    if _is_meaningful(p) and not _looks_like_hours(p)
                ]

                if len(parts) >= 2:
                    address = parts[-1]
                    break

        # --- Final safety net ---
        # No matter which path produced these, never let an
        # hours-shaped string end up in category or address.
        if category and _looks_like_hours(category):
            category = None
        if address and _looks_like_hours(address):
            address = None

        return category, address