# Preparation review and freeze checklist

Status: **PREPARATION ONLY / all gates NOT_RUN**. Source review is static, not
verification credit. No tool/source delta or new runtime policy is introduced.
No Kani source/test files owned by worker14 are changed; no old receipts edited.

Before final authorization, coordinator must:

1. Freeze accepted C1 including E2 immutable-edge repair and M3/mixed-order
   qualification. Record exact SHA/tree, clean diff from C0, compiler/library/
   tests subtrees and required file SHA-256s. Any new source delta invalidates
   affected receipts; gate only final export.
2. Recreate CI-only overlay on C1; preserve export tree and all regression
   inputs. Bind schema/format and complete required files/subtrees, set
   m3_accepted=true only with explicit acceptance evidence. Never substitute C0
   baseline hashes just to satisfy the preflight.
3. Review eight strong oracles on the final export and six mode expectations,
   including useful SUCCESS and exact negative identities, not just exits:

| Strong oracle ID | Required interpretation |
| --- | --- |
| p1 | initialized-return useful outer ensures SUCCESS |
| ordinary | body, ensures and harness useful assertions SUCCESS |
| pfc | actual Check body, ensures, harness and selected out assigns SUCCESS |
| lawful-modifies | useful result29/out29/outside41 and selected assigns SUCCESS |
| p2 | exactly two specified u8 read checks; exact ensures consequence only |
| postcondition-hole | paired two read checks on different frozen source input |
| frame | singleton user outside-assigns failure; lawful out write SUCCESS |
| clause | specified MaybeUninit<u16> read in requires helper, no substitute |

C0 source of truth is `tests/json-handler/uninit-contract-oracles/oracles.json`
(hash in EXPORT-MANIFEST). p2 and postcondition-hole share a harness spelling
but have distinct input hashes/locations; do not collapse them.

| Mode harness | C0 manifest expected result |
| --- | --- |
| replace_transfer | UNCLAIMED; no Replace shadow-transfer support inferred |
| replace_ordinary | SUCCESS plus exact initialized/uninitialized covers |
| replace_simple_check | SUCCESS plus the same mode-specific covers |
| recursive_check | UNSUPPORTED_INTERPROCEDURAL_CYCLE; not proof |
| recursive_ordinary | UNSUPPORTED_INTERPROCEDURAL_CYCLE; not proof |
| recursive_simple_check | SUCCESS plus base/unrolled edge and payload covers |

C0 mode manifest is `tests/json-handler/uninit-contract-mode-boundaries/roots.json`
(hash in EXPORT-MANIFEST). Read final C1 manifest rather than silently applying
these baseline expectations to changed tests. M3/mixed qualification is a
separate acceptance item with new exact roots/oracles supplied by worker14;
neither Quick C0 nor Gate A replaces it.

4. Confirm final SmallSort library pin with coordinator, create test-only replay
   overlay separately, bind all cfg/argv/root/check-body/control locations. The
   maps record the contracts-ON negative boundary. A failed requires or an
   unrelated raw probe cannot satisfy the retained actual-helper read oracle.
5. Grant run phase/owner/lane, cap/slot/deadline and budget explicitly. The
   proposed Linux Gate A workflow has no new run permission. Gate B needs its
   own existing coordinator lane and exact binary/model hashes from accepted
   C1 build, separate ON/OFF/control receipts, matching source/geometry.
6. Validate Gate A stage coverage/counts/exits and Gate B actual useful checks,
   exact failures, contract modes, all ON roots and matched OFF companions.
   Source claims, static inventory, B1 bounded replay and any B2 full proof
   must be reported separately; Unsupported and expected reproducer failures
   never gain formal proof credit.

Python observer review by a bounded Luna HIGH helper identified incomplete
binding validation and pre-setup failure artifacts; those are fixed. Full
source identity checks now run before dependency setup, and an always step
retains a NOT_RUN/partial receipt plus job status on early failure. Actual
Bash hook/runtime inventory behavior remains CI-unqualified; synthetic tests
exercise only the observation protocol and strict source-binding validator.
If shell trace, counts or upload is incomplete, preserve GAP/UNKNOWN and do
not infer stage acceptance. Runtime bytes are outputs of Gate A, inventoried
for later replay binding, not assumed known before the C1 build.

Static output-format check: C0 tools/compiletest/src/main.rs:277-309 uses
Rust test::run_tests_console, and exits1 on test failures or panics on I/O
failure; quiet selects Terse. Receipt retains each libtest summary plus numeric
passed/failed/ignored/measured/filtered counts. A failed test is explicitly an
unexpected test/oracle failure; an intended verifier negative is accepted only
through its unchanged frozen test oracle. Exact negative property acceptance
still belongs to the eight-oracle/mode receipts, not aggregate suite counts.
The ordinary Kani default solver is CaDiCaL (call_cbmc.rs:103-105), not the
installed/version-checked Kissat dependency. Replay uses that default.

Final static validation: `python3 -B validate_package.py` (from this directory,
or use its repository-relative path) passes; 11 synthetic Python tests pass.
It checks frozen source hashes, clean read-only inputs and own overlays,
exact overlay patch identities and bounded write scopes, ON/OFF argv equivalence,
YAML syntax/dispatch-only trigger, and disabled pending final inputs. This does
not compile either overlay or execute the shell observation hook.

Whitespace note: research `git diff --cached --check` flags two literal removed
upstream workflow lines inside ci-only-overlay.patch (artifact lines103/130).
The exact patch bytes are retained for applicability/hash integrity. Both real
overlay diffs pass `git diff --check BASE HEAD`; research files excluding patch
artifacts also pass. These are inherited artifact text, not source changes.
