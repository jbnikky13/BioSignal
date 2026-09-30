"""Runtime retrieval of public WHO GLASS-AMR CSV data."""

from io import StringIO
from urllib.request import Request, urlopen

from .sources import who_glass_amr_url


def fetch_csv(
    *,
    columns: list[str] | None = None,
    filters: str | None = None,
    top: int | None = None,
    timeout: int = 30,
) -> str:
    """Fetch a public CSV response without storing it in the repository."""
    url = who_glass_amr_url(columns=columns, filters=filters, top=top)
    request = Request(url, headers={"User-Agent": "BioSignal/0.1"})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def parse_csv(text: str) -> list[dict[str, str]]:
    import csv
    return list(csv.DictReader(StringIO(text)))
