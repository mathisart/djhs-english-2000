# Vocabulary import pipeline

## Input
An official/approved source and its source metadata.

## Pipeline
1. Archive source/version metadata.
2. Parse source entries without changing meaning.
3. Normalize canonical word IDs (case/spacing/variant policy).
4. Preserve source-specific POS, Chinese gloss, notes, and level separately.
5. Match against the master vocabulary.
6. Create only genuinely new master words.
7. Create list-membership relations for existing/new words.
8. Generate a diff report: added, removed, changed, ambiguous, unmatched.
9. Human-review ambiguous/unmatched items.
10. Validate counts and invariants.
11. Mark the snapshot verified.
12. Only then switch production pools.

## Required validation
- source is identifiable and versioned
- no duplicate canonical membership inside a list
- expected list structure/counts are explained
- every list item resolves to a master word
- variants/phrases are explicitly handled
- source-specific information is not overwritten by another source
- production list never falls back to difficulty-derived membership

## Future list import
New lists (e.g. TOEIC, senior-high vocabulary, school exam lists) use this same pipeline. If an exam owner does not publish an official vocabulary list, label the dataset derived/curated rather than official.

## Student progress invariant
Mastery is keyed to canonical word ID, not to list/version. Updating list membership must not erase mastery.
