# Official vocabulary QA gates

Production may switch to an official snapshot only when every required gate passes.

## Source gates
- [ ] Issuing authority confirmed.
- [ ] Official source URL pinned.
- [ ] Release/revision date recorded.
- [ ] Raw snapshot/version retained or reproducibly retrievable.
- [ ] Source trust is explicitly classified.

## Parsing gates
- [ ] No silently rejected blocks.
- [ ] Page headers/footers removed.
- [ ] Wrapped rows reconstructed.
- [ ] Multi-POS entries preserved.
- [ ] Source notes and AWL markers preserved where available.
- [ ] GEPT membership comes from row-level official level.
- [ ] MOE 2000 is derived from basic 1200 + other common 800.
- [ ] Recognition-only country/festival names are not miscounted as basic 1200.

## Identity gates
- [ ] Canonical IDs are stable.
- [ ] Case and whitespace normalization is deterministic.
- [ ] Aliases/variants do not create accidental duplicate master words.
- [ ] Phrases remain phrases when the official source treats them as entries.
- [ ] Same spelling with multiple senses/POS remains one master word with source senses.

## Migration gates
- [ ] Existing student mastery is mapped by canonical word ID.
- [ ] Removed list membership never deletes mastery.
- [ ] New words do not inherit another word's mastery.
- [ ] Current 2055 candidate pool is diffed, not blindly overwritten.
- [ ] Added/removed/shared/unmatched counts are reviewed.
- [ ] POS/gloss conflicts are reported.
- [ ] Production UI labels match the actual verified list.

## Unlock gates
- [ ] GEPT Intermediate remains unlockable, not public by default.
- [ ] GEPT High-Intermediate requires Intermediate first.
- [ ] UI says B1/B2 vocabulary challenge, not CEFR proficiency certification.
- [ ] Unlock rules are based on genuine mastery breadth, not raw XP farming.

## Release
A release report must record source versions, validation counts, unresolved exceptions,
migration effects, and the exact commit that activates the new pools.
