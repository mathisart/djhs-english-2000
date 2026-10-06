# Official vocabulary data

This directory stores versioned source manifests and normalized official word-list snapshots.

## Rules

1. Prefer the issuing organization's current official source.
2. Never silently overwrite an old official snapshot; add a new version.
3. Preserve source metadata separately from learning content.
4. A word exists once in the master vocabulary. Word lists reference canonical word IDs.
5. Official list membership is not inferred from difficulty.
6. AI may parse, normalize, compare, and flag anomalies, but uncertain items require review.
7. Production pools change only after validation reports pass.

## Source trust

- official: published by the issuing authority
- derived: derived from an official specification, but not an official published word list
- curated: reviewed educational compilation
- custom: teacher/school-created list

## Visibility

- public: selectable by students
- unlockable: hidden until learning requirements are met
- hidden: stored but not exposed in the UI
