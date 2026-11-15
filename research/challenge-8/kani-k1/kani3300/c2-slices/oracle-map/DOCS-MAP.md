# Docs ownership — final coordinates in F

DOCS-MAP.json assigns every added line/character span and every removed U line once. Shared physical hunks are split by sentence, never restored as whole files.

| File / final F location | Owner / earliest feature | Required meaning |
|---|---|---|
| rust-feature-support.md:180–184 before Qualified |4|Storage shapes, typed data/padding, ordinary executing MIR-body argument/return protocol|
| rust-feature-support.md:184 Qualified…192 |2|Exact whole immutable qualification, Freeze/layout/extent/offset0, unqualified subrange/relocation false positives and qualified aliases|
| rust-feature-support.md:198–200;202–203 |4|Hook-only exclusion, Fn-item shim limits and F6 nested aggregate reset; mode connector/reflow in6|
| rust-feature-support.md:194–197;201;204–208 |6|General Scope A limits, contract links, mode/cycle/SmallSort exclusion; don't insert the complete scope promise early|
| contracts.md:73;76–78 before Whole;95–106 |4|Heading, ordinary direct protocol and conservative full reset destination normal return / moved source before call; known tuple-return false positive|
| contracts.md:78 Whole…81 |2|Immutable qualification reference and conservative alias limits|
| contracts.md:74–75;82–94;107 |6|General limitation linkage, Replace/RecursiveCheck/cycle limits, local companion presence vs execution|
| intrinsics.md:197 raw_eq row |3|Both modeled raw byte extents including padding, layout/origin qualification; no unconditional promise|
| part1-edges/README.md entire file |6|Semantic edge guidance, legal subrange false positive, relocation/static companions and unsized-by-value boundary|

At2 publish a self-contained immutable paragraph using only its text; at4 compose the storage text; at6 apply final exact F wrapping/link placement. An inserted partial paragraph must not advertise future features or leave a dangling contracts limitations link. Final shared-line wrapping is explicitly accounted; no final textual deviation permitted.

There is no separate explicit closure-limit sentence added in F. At5 the computable-mask qualification already bounds closure support; do not invent closure documentation or claim union/UnsafeCell capture admission. Exact masks/upvar-offset claims belong to the test/source map. Source README comments are fixture-owned and travel with their test.

No research paths/run IDs/CI receipts/process prose in export. Native docs build and intermediate rendered link checks NOT_RUN; static final links point at existing F sections.
