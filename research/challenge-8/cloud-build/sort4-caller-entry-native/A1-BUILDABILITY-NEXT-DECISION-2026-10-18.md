# Owner decision requested — bounded parser diagnostic audit

Task select-sort4-ocaml-buildability-2026-10-18-r1. Active windowmain20:59:16Z,
absolute21:29:16Z. No parser/admission semantics change or raw access authorized
by this request. R5Build87df47e4-002b-432c-bc87-56612136b448,source6f3abaa4.

Ordinary Brief reports P0a InventoryError: decoded VfMir parse failed: invalid
quoted string at byte9362; source proof-auditSHA256
81414bda84c65ced707c66e720f3c26938b4dd321e920952065807635e838769.
It exposes mixed aggregate26(8INTENDED_CLASSIFIED/5INCONCLUSIVE/13NOT_RUN), but
not named individual statuses or successful ownreference receipt content/hash.
Normal agent has read only Brief; source claims and integrity are not proof.

Static code: a1-compiler-inventory._find_vfmir calls the bounded parser in
[a1-synthetic-inputs.py](a1-synthetic-inputs.py). _Parser._string sends the quoted
literal to json.loads and reports any decoder error at self.i start. Actual
literal/field/escape at9362 and JSON decoder reason are not exposed by Brief.
The index is a Python str index despite message saying byte; an audit must check
UTF8 byte versus Unicode-character offsets. We cannot select the actual fix from
a guessed escape, and grammar changes feed source/admission identity checks.
This is beyond compile-only R annotation/small build-wiring scope; task section2
freezes decoder/admission predicates and requires separate scope decision.
No new Build may be used merely to bypass missing reporting.

## Requested separate administrative audit, only after explicit authorization

No compiler/exporter/decoder/refiner/verifier execution and no Build. Use existing
immutable R5 evidence for a compact administrative deliverable:

1. Exact failing quoted literal and field at reported9362, at most±160characters
   context (≤30raw lines total). Provide Unicode and UTF8 byte offsets, the escape
   bytes in hex where relevant, exact JSON decoder error and file/member SHA256.
   Distinguish truncation/malformed input from valid printer syntax unsupported by
   current parser. Do not infer that the literal contains a particular escape.
2. Named26case statuses with original source provenance, first P0a error chain and
   observed last substage where evidenced. Unknowns remainUNKNOWN; do not assign
   NOT_RUN from absence, do not turn INTENDED_CLASSIFIED into formalcredit.
3. New R-only tool reference receipt and final C tool receipt facts/hashes, tied
   to Build/source/profile/compiler identities. P1 own reference equality receipt
   and N-false31 own-pair lifecycle facts separately, or explicit not-exposed.

Suggested total deliverable≤16KiB,≤30rawlines,fullSHA256 references; ordinaryagent
should receive the compact audited result rather than full archives/logs. No
raw fallback is permitted while authorization is pending.

## Subsequent scope decision after that diagnostic

If valid source printer escaping is the cause, consider a separately authorized
bounded string-parser compatibility fix with exact accepted/rejected synthetic
cases, unchanged shape/identity/admission predicates, source closure/pins andLuna
review. No implementation is included or implicitly authorized here. Decoder,
compiler,contracts,G/kernel/prelude/refiner and source source domains stay frozen.
