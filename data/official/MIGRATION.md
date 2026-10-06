# Student mastery migration contract

## Stable key
Learning state belongs to a canonical vocabulary identity, never to:
- array position
- current list
- current difficulty
- current source version
- current UI mode

## List changes
If a word moves between official lists, its mastery remains unchanged.
If a list is removed, mastery is retained.
If a new list includes an already-known canonical word, that word reuses existing mastery.

## New official words
A canonical word absent from the previous master starts with no mastery. It must never inherit
progress from a neighboring row, similar spelling, alias guess, or previous array index.

## Removed current words
A word absent from a new official list is not automatically deleted from learner history.
It may remain as legacy/content vocabulary while losing that official membership.

## Identity changes
Spelling variants or aliases require an explicit migration decision. Automatic stemming,
edit-distance matching, or semantic similarity is insufficient to transfer student progress.

## Release evidence
Before activation, run `tools/check_mastery_migration.py` and review:
- shared canonical IDs
- old-only IDs
- new-only IDs
- duplicate IDs
Any deliberate alias transfer must be recorded as a reviewed mapping artifact.
