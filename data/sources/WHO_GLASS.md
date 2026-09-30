# WHO GLASS-AMR mapping notes

BioSignal uses the WHO GLASS RELAY_GLASS_AMR relay table as a public source.

The WHO dashboard code exposes dimensions such as:
- DIM_GEO_CODE_M49
- DIM_MEMBER_1_CODE
- DIM_MEMBER_2_CODE
- DIM_MEMBER_3_CODE
- IND_CODE
- VALUE_NUMERIC
- VALUE_LABEL

BioSignal intentionally does not guess that an indicator code or member code means a particular pathogen, antimicrobial, period, or resistance metric.

A production mapper must join these codes to the appropriate WHO reference metadata and document the mapping version.

Official documentation:
- WHO GLASS-AMR: https://www.who.int/initiatives/glass/glass-routine-data-surveillance
- WHO GLASS manual: https://www.who.int/publications/i/item/9789240076600
