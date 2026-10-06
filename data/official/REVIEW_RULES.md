# Human review rules

Automated diffs produce evidence; they do not authorize semantic rewrites.

## Safe automatic operations
- Unicode/spacing normalization
- exact canonical ID match
- official list membership attachment
- retention of all official source rows/senses
- derived-list membership defined by manifest

## Must be reviewed
- spelling variants not explicitly supplied by the source
- one official entry matching multiple master records
- one master record matching multiple unrelated official entries
- POS disagreement
- phrase vs single-word identity
- punctuation that changes lexical identity
- official rows rejected by the parser
- additions/removals between official versions

## Chinese meanings
The current app Chinese gloss and the official/source gloss may differ in granularity.
A difference is evidence for review, not permission to overwrite the learner-facing gloss.
Source glosses stay in sourceEntries; curated app glosses stay in CONTENT.

## Multi-sense words
One canonical word may have multiple source entries. Never collapse source senses merely
to make counts look cleaner. Word-level mastery remains shared unless a future learning
design explicitly introduces sense-level mastery.

## Decision log
Every non-trivial merge/split/alias decision should be reproducible in a review artifact,
not hidden inside code or an AI conversation.
