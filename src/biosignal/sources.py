"""Public data-source definitions for BioSignal.

The WHO GLASS dashboard documents that global AMR data are retrieved from
the XMART RELAY_GLASS_AMR table. BioSignal keeps the endpoint definition
explicit so ingestion remains auditable and reproducible.
"""

from urllib.parse import urlencode

WHO_GLASS_AMR_ENDPOINT = "https://xmart-api-public.who.int/DATA_/RELAY_GLASS_AMR"

WHO_GLASS_SOURCE = {
    "name": "WHO GLASS-AMR",
    "publisher": "World Health Organization",
    "endpoint": WHO_GLASS_AMR_ENDPOINT,
    "documentation": "https://www.who.int/initiatives/glass/glass-routine-data-surveillance",
}


def who_glass_amr_url(
    *,
    columns: list[str] | None = None,
    filters: str | None = None,
    top: int | None = None,
    csv: bool = True,
) -> str:
    """Build a reproducible WHO GLASS XMART AMR query URL."""
    params: list[tuple[str, str]] = []
    if columns:
        params.append(("$select", ",".join(columns)))
    if filters:
        params.append(("$filter", filters))
    if top is not None:
        params.append(("$top", str(top)))
    if csv:
        params.append(("$format", "csv"))
    return WHO_GLASS_AMR_ENDPOINT + ("?" + urlencode(params) if params else "")
