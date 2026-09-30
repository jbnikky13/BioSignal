# BioSignal data sources

## WHO GLASS-AMR

BioSignal's first external data-source adapter targets the WHO Global Antimicrobial Resistance and Use Surveillance System (GLASS).

WHO describes GLASS-AMR as a standardized system for collecting, analyzing and sharing AMR surveillance data. The current GLASS dashboard repository documents that global AMR dashboard data are retrieved from the RELAY_GLASS_AMR XMART table.

Sources:
- WHO GLASS-AMR: https://www.who.int/initiatives/glass/glass-routine-data-surveillance
- WHO AMR portal: https://data.who.int/dashboards/amr/overview
- WHO GLASS dashboard source: https://github.com/WorldHealthOrganization/GLASS-Dashboard

BioSignal does not copy the WHO production database into this repository. The adapter records the public endpoint and query construction so a controlled ingestion job can retrieve data at runtime and preserve source metadata.

Every imported dataset should record source name, endpoint, retrieval timestamp, query/filter, schema version, transformation version, row count, and a checksum when a raw artifact is stored.

Do not commit patient-level or restricted data.
