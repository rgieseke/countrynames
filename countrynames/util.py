from collections.abc import Iterator
from normality import normalize


def normalize_name(country: str | None) -> str | None:
    """Clean up a country name before comparison."""
    return normalize(country, latinize=True)


def process_data(data: dict[str, list[str]]) -> Iterator[tuple[str, str, str]]:
    """Load known aliases from a YAML file. Internal."""
    for code, names in data.items():
        code = code.strip().upper()
        norm_code = normalize_name(code)
        if norm_code is not None:
            yield code, norm_code, code
        for name in names:
            norm_name = normalize_name(name)
            if norm_name is not None:
                yield code, norm_name, name
