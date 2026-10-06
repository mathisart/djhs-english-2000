# Official vocabulary release policy

## Freshness gate
An official vocabulary snapshot cannot become active unless:
1. the issuing authority's current official page has been checked;
2. the current revision/publication date has been recorded;
3. the retrieval/check date has been recorded;
4. superseded versions remain identifiable;
5. a version-to-version diff is reviewed when a prior snapshot exists.

If a newer official revision is discovered, the older snapshot is automatically non-active
until the newer source completes parsing, validation, anomaly review, and migration QA.

## Activation gate
Production activation requires all of:
- source freshness PASS
- parser rejection review PASS
- structural/count validation PASS
- official-to-master diff reviewed
- canonical identity migration reviewed
- unresolved anomalies explicitly documented
- student mastery preservation verified
- release report generated

## No silent assumptions
Expected counts (such as “1200” or “2000”) are validation targets, not permission to add,
remove, merge, or guess entries merely to make a number match.

## Rollback
Activation must be a separate commit from data ingestion. The previous active catalog/version
must remain recoverable so production can be rolled back without touching student mastery.
