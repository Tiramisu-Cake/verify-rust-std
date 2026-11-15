# Worker14 rework handoff — slice03

Source `5ca51679e3f433718807a2e44add0d5abac128e7` has accepted2
`932fb8395a58f8c86c0d702ba2cae835823b2962` as its sole parent.
Worker15 review of this rewritten head and exact-head Quick remain **PENDING**.
Local native builds, push and CI: **NOT_RUN**.

Coordinator decision: [historical run43704461635](ci-43704461635/RESULT.md).
The old source d0345ddf4f / overlay a2a533e087 built and passed its previous
regression controls, but18 newly introduced fixtures hit early Unsupported.
This is a source-reported coordinator result, not a result for the rewritten head.
The stage0 placement was incorrect: nonempty MaybeUninit arrays and raw-pointer/union
interaction require storage4. Their fixture owner and first executable head are now4.

The rewritten commit removes exactly those18 newly added input/golden pairs.
Production and docs are byte-identical to d0345ddf4f. A1/A2, both RawEq byte extents,
reference CheckAs, both relevance seeds and the UintTy neutral import are unchanged.
No existing accepted2 test, directive, assertion, ignore or golden is changed.
`immutable-masks/empty` is the sole new pair: exact F, zero extent, owner2/head3.
Its success does not qualify nonempty MU storage or the layout/raw integration targets.

Qualification kind is **NO_REGRESSION**; integration remains **PENDING on4**.
DEFERRED-OBLIGATIONS.json contains the18 reassigned complete fixtures plus the prior
nine owner3 obligations: nested Pat/enum, raw-eq-uninit and four raw-MU mixed cases.
All preserve exact F source/golden identities and intended oracle precision; none is
introduced early, ignored or given an Unsupported golden. Owner1 integration stays
PENDING on4/5, with historical receipts untouched.

Canonical oracle/source maps belong to their original owners and remain unchanged.
ORACLE-MAP-CORRECTION.json explicitly overrides fixture and path ownership/head for18
pairs. Future4 extraction must apply it together with SOURCE-MAP-CORRECTION.json
(the existing neutral import delta); production ownership has no new change.
The old source/package/review remain in Git; the failed run record is retained.

FIXTURE-DEPENDENCY-AUDIT.json checks the actual tree, including cumulative additions
since B1. Six inherited initialized-u8 descriptor probes and the zero-extent fixture
are the only new inputs. All mapped future fixtures are absent except four unchanged
B1 unresolved-calls entry controls, whose target integration remains pending4.
The inherited function-item/drop-glue closure probes remain regression controls;
no new closure mask/layout fixture is imported. Token/manual checks are static only.

STATIC-VALIDATION.json checks all22 source parts, exact extraction, unchanged production,
protected ancestors, F fixture bytes and both alternate-index patch endpoints.
The residual reaches F's exact tree; it does not qualify or compose future heads4–7.
No native proof or formal proof credit is claimed. Next: worker15 exact-head review
and preparation of a new CI-only overlay; coordinator owns dispatch/acceptance.
