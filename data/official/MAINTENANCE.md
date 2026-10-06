# Adding or updating a vocabulary list

This is the maintenance runbook for humans and AI agents.

## Add a new source/list

1. Confirm whether the issuing organization actually publishes a vocabulary list.
2. Add/update the source in `data/official/sources.json`.
3. Add the list definition in `data/official/lists.json`.
4. Store or retrieve the versioned raw source reproducibly.
5. Write/reuse an importer that preserves source-level fields.
6. Normalize to a snapshot with `verified: false`.
7. Run `tools/validate_official.py`.
8. Run `tools/diff_official.py` against `words.js`.
9. Review every rejected/ambiguous/unmatched item.
10. Record exceptions and resolutions.
11. Only after review, set the snapshot to `verified: true`.
12. Build the catalog with `tools/build_catalog.py`.
13. Run gameplay regression checks.
14. Activate the list in production in a separate commit.
15. Bump frontend asset version if JS/data changed.

## Update an existing official source

Never overwrite the previous version. Add the new snapshot, run a version-to-version diff,
review additions/removals/changed senses, then switch the active version.

## AI instruction template

> Add/update <LIST NAME>. Use the issuing organization's newest official source where one
> exists. Preserve the previous version. Run validation and diffs. Do not label a
> third-party/AI compilation official. Do not activate production until unresolved items
> are reviewed. Preserve student mastery by canonical word ID.

## Visibility policy

- public: immediately selectable
- unlockable: revealed only after learning requirements
- hidden: data available but never shown to students
- internal: implementation component, such as MOE other-common 800

## CEFR policy

CEFR alignment and exam-list membership are separate concepts. Passing an app vocabulary
challenge must never be described as certification of the student's overall CEFR level.
