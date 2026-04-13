import logging
from functools import lru_cache
from rapidfuzz.distance import Levenshtein

from countrynames.mappings import mappings
from countrynames.util import normalize_name, process_data


log = logging.getLogger(__name__)

__all__ = ["to_code", "to_code_3"]

COUNTRY_NAMES: dict[str, str] = {}


def _load_data() -> dict[str, str]:
    """Load known aliases from a YAML file. Internal."""
    from countrynames.data import DATA

    names: dict[str, str] = {}
    for code, norm, _ in process_data(DATA):
        names[norm] = code
    return names


def _fuzzy_search(name: str) -> str | None:
    best_code = None
    best_distance = None
    for cand, code in COUNTRY_NAMES.items():
        if len(cand) <= 4:
            continue
        distance = Levenshtein.distance(name, cand)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_code = code
    if best_distance is None or best_distance > (len(name) * 0.15):
        return None
    log.debug(
        "Guessing country: %s -> %s (distance %d)", name, best_code, best_distance
    )
    return best_code


@lru_cache(maxsize=None)
def to_code(
    country_name: str | None, fuzzy: bool = False, default: str | None = None
) -> str | None:
    """Given a human name for a country, return a two letter code.

    Arguments:
        ``fuzzy``: Try fuzzy matching based on Levenshtein distance.
    """
    # Lazy load country list
    if not len(COUNTRY_NAMES):
        COUNTRY_NAMES.update(_load_data())

    if country_name is None:
        return default

    # shortcut before costly ICU stuff
    country_name = country_name.upper().strip()
    # Check if the input is actually an ISO code:
    if country_name in COUNTRY_NAMES.values():
        return country_name

    # Transliterate and clean up
    name = normalize_name(country_name)
    if name is None:
        return default

    # Direct look up
    code = COUNTRY_NAMES.get(name)
    if code == "FAIL":
        return default

    # Find closest match with spelling mistakes
    if code is None and fuzzy is True:
        code = _fuzzy_search(name)
    return code or default


def to_code_3(country_name: str | None, fuzzy: bool = False) -> str | None:
    """Given a human name for a country, return a three letter code.

    Arguments:
        ``fuzzy``: Try fuzzy matching based on levenshtein distance.
    """
    code = to_code(country_name, fuzzy=fuzzy)
    if code is None or len(code) > 2:
        return code
    else:
        return mappings[code]
