import re
from difflib import SequenceMatcher
from typing import Iterable, Optional

from app.models.business import Business

# Similarity above this = treated as the same business.
DUPLICATE_THRESHOLD = 0.90

# Looser threshold for addresses, since formatting varies more
# ("Plot 17/18, Zen's Den, ..." vs "Zen's Den, Plot 17/18, ...").
ADDRESS_THRESHOLD = 0.60


def is_valid_business(business: Business) -> tuple[bool, str]:
    """Basic sanity checks before saving.

    Returns:
        (True, "") if valid.
        (False, reason) if not.
    """
    if not business.name or not business.name.strip():
        return False, "missing name"

    if not business.maps_url:
        return False, "missing maps_url"

    if business.rating is not None:
        if not (0 <= business.rating <= 5):
            return False, f"invalid rating: {business.rating}"

    return True, ""


def normalize_name(name: str) -> str:
    """Strips branch suffixes, punctuation, and casing so that
    "Ginsoy - Bahria Town Branch" and "Ginsoy (Bahria Town)" match
    as the same base business."""
    name = name.lower()

    # Remove common branch-suffix patterns: "- Branch Name", "(Branch Name)"
    name = re.split(r"[-(]", name)[0]

    # Remove non-alphanumeric characters.
    name = re.sub(r"[^a-z0-9\s]", "", name)

    return name.strip()


def normalize_address(address: str) -> str:
    """Lowercases and strips punctuation for loose comparison."""
    address = address.lower()
    address = re.sub(r"[^a-z0-9\s]", "", address)
    return address.strip()


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _first_word(text: str) -> str:
    words = text.split()
    return words[0] if words else ""


def find_near_duplicate(
    name: str,
    address: Optional[str],
    existing: Iterable[tuple[str, Optional[str]]],
) -> Optional[str]:
    """Checks a new business against already-known (name, address)
    pairs.

    Same/similar name alone isn't enough — many businesses share
    generic names (e.g. "Dental Square") across different areas.
    A name match only counts as a duplicate if the address also
    matches. If either address is missing, falls back to
    name-only matching (can't verify, so treat as duplicate to
    avoid piling up obvious repeats).

    Returns the matching existing name if a near-duplicate is
    found, otherwise None.
    """
    normalized_name = normalize_name(name)
    normalized_address = normalize_address(address) if address else None

    for existing_name, existing_address in existing:
        existing_normalized_name = normalize_name(existing_name)

        name_match = (
            _similar(normalized_name, existing_normalized_name)
            >= DUPLICATE_THRESHOLD
            and _first_word(normalized_name)
            == _first_word(existing_normalized_name)
        )

        if not name_match:
            continue

        # No address on one/both sides: can't verify, fall back
        # to name-only match.
        if not normalized_address or not existing_address:
            return existing_name

        existing_normalized_address = normalize_address(existing_address)
        address_match = (
            _similar(normalized_address, existing_normalized_address)
            >= ADDRESS_THRESHOLD
        )

        if address_match:
            return existing_name

        # Same name, different address -> likely a different
        # branch/location, not a duplicate. Keep checking others.

    return None