# S1-07 — 22 exact PFC chains, Profiles v4 component

Run `43923266772`; task commit `2f3ede5ff46ace1c2058f01f8ecda06799674b57`.
**22 SOURCE_REPORTED_BOUND / 0 PENDING**, including 20 production rows
(two legal companions) and two activation variants. This is a PFC component,
not an admission-root verdict. No overall qualified count is recomputed.
Independent compiler/general/B1/B2 proof credit: **NONE**. Separate w14 review
remains the coordinator's next stage.

## Identities and replay

- std: `5be85699b8826e3286c0bf89efb9affefac0acb5`.
- stock tool: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- executed control namespace: `b37f6f75c5b7b77e84297cd7104f9c0868502fd4`.
- exact request SHA256: `6c483ce754cd8e99c01953bf4c40a145b10529d7990aa52c28ef32c00b980cd7`.

`python3 -B replay.py` reconstructs the component and compares PFC.json byte for
byte; `--write` writes only that file. Run from this directory, or use the full
script path. `python3 -B -m unittest discover -s . -p test_replay.py` runs the
synthetic suite. VALIDATION.json records two matching replays, test results and
code/output hashes. All input bytes are compared with task-commit Git objects;
source and producer reads use their pinned Git objects. The 67 input hashes,
source dependency hashes, source excerpts, six raw→decoded entries and demangler
identity are retained in PFC.json. No artifact is copied into this directory.
The compile receipt's original-member hash and reserialized projection hash are
distinct, checked against pinned PROVENANCE.json, and never conflated.

## Chain and semantics

The method follows [Profiles v4](../../../../ch8-profiles/off-ci-batch/run-43784551069/accept-v4/BINDING.md).
Every row is reconstructed from exact request group/variant, complete group
export and rich property inventories, crate/harness selector, source macro
invocation (or direct attribute), and embedded native metadata. Native content
length/hash and JSON pointer are checked. The manual `contracted_functions`
record must contain that exact harness once and the exact generic target
definition `<T as slice::sort::shared::smallsort::<trait>>::small_sort` and file.
Native and export attributes, raw contract symbols and source sites must agree.
Compile boundary, exact argv/cfg/checks/unwind, source snapshots, effective variant
hashes and matching before/after binary snapshots retain the same-run namespace.
Runner invocation identity does not become a compiler instance identity.

Pinned producer source establishes these edges:

1. `contracts/mod.rs:572–587` preserves the PFC target; `resolve.rs:58–119`
   resolves it; `metadata.rs:81–95` groups manual harnesses by target definition;
   `codegen_units.rs:282–288` records Check(target).
2. `initialize.rs:72–90` names generated closures; `bootstrap.rs:32–105` attaches
   `checked_with` and `modifies_wrapper` and selects SIMPLE_CHECK.
3. `check.rs:23–80,84–120,135–153` assumes requires, passes modifies addresses
   into the wrapper containing the original body, then asserts ensures with the
   source clause string. PFC requires have **no asserted property IDs** here.
4. `codegen/contract.rs:19–52,98–124` resolves the target's named checked_with,
   then its named modifies_wrapper. `AssignsContract.contracted_function_name`
   is the latter's mangled name. `call_goto_instrument.rs:177–212` passes that
   exact symbol as the sole `--enforce-contract`; each exact harness has no loop
   contracts or stubs. Thus frame checks are write sites under that contract.
5. `cbmc_output_parser.rs:132–139,280–307` explains property IDs and locations.
   Full property stems and location functions are compared to the decoded
   wrapper, preserving every module and generic argument. Only local `core::`
   prefixes are normalized. Clauses normalize whitespace only.

The raw symbol must occur **exactly twice in each** of the two retained
`single_top_level_call` / `no_recursive_call` descriptions. Both must be SUCCESS,
at the selected impl's exact modifies site, with the complete decoded wrapper
stem. Its parent check closure must contain the exact ensures expression, site,
ID and expected status. Role assignment never uses a closure index: structural
nesting is read only after the producer establishes the raw-symbol role. A
synthetic coherent renumbering confirms that no #2/#1 role gate was introduced.
No suffix-only comparison is used.

The pair is not a substitute for clauses: PFC.json separately records every
assumed requires clause, asserted ensures property, enforced modifies clause,
all retained assigns/frees write-site checks and both allocation diagnostics.
The write-site checks and allocation diagnostics are SUCCESS for all 22 rows.
Their exact property IDs are retained; no source-reported status is rewritten.
Other U/caller/role/cover gates remain outside this component.

## Source specialization

The selected header, method and all contract attributes come from the effective
`library/core/src/slice/sort/shared/smallsort.rs`, not from terminal method names.
All six impls are distinguished by trait, concrete type, bounds, source sites
and the complete `KeyLess<T>` instance. Source type-system facts are interpreted
under the expressly trusted pinned stock compiler:

- `shared/mod.rs:3–13`: FreezeMarker is implemented for Freeze types.
- `cell.rs:311–317`, `marker.rs:905–919`: Cell contains UnsafeCell, which has the
  negative Freeze impl. Cell<u8> therefore uses the unbounded defaults.
- `marker.rs:473–480`: u8 implements Copy; it is Freeze. The CopyMarker blanket
  impl (`smallsort.rs:153–160`) selects the Copy specialization for the freeze
  trait; other two traits select their Freeze specialization.
- `sorting_model.rs:13–27`: NonCopyByte is a transparent u8 wrapper with no Copy
  derive/impl; its Freeze/non-Copy specialization is the freeze default.
  `:47–64,139–154` binds KeyLess and the active model instances.
- `smallsort.rs:195–218` anchors thresholds 16/32 and scratch geometry. Each
  macro's type, trait, threshold, route and exact N (when split) are checked.

These source facts, matching decoded instance, native target-definition link and
selected impl's exact property sites jointly establish the chosen source-reported
binding. No independent rustc resolution trace is claimed.

## Exact rows

The sites below are effective-source lines in smallsort.rs; full property IDs,
descriptions and location functions are in each JSON binding. Every row also has
both exact raw-symbol diagnostics SUCCESS. `Stable`, `Unstable`, `Freeze` mean
StableSmallSortTypeImpl, UnstableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl.

| Row | Group | Type / trait | Impl / modifies / ensures line | Ensures |
|---|---|---|---|---|
| `activation-default` | `activation-default-u34` | `Cell<u8>` / Stable | 32 / 40 / 41 | FAILURE |
| `activation-override` | `activation-override-u34` | `u8` / Stable | 54 / 62 / 63 | FAILURE |
| `freeze_copy_u8_n0` | `freeze_copy_u8-n01-u34` | `u8` / Freeze | 160 / 175 / 176 | SUCCESS |
| `freeze_copy_u8_n1` | `freeze_copy_u8-n01-u34` | `u8` / Freeze | 160 / 175 / 176 | SUCCESS |
| `freeze_copy_u8_n2` | `freeze_copy_u8-n23-u34` | `u8` / Freeze | 160 / 175 / 176 | SUCCESS |
| `freeze_copy_u8_n3` | `freeze_copy_u8-n23-u34` | `u8` / Freeze | 160 / 175 / 176 | SUCCESS |
| `freeze_default_noncopy_n0` | `freeze_default_noncopy-n01-u34` | `NonCopyByte` / Freeze | 128 / 139 / 140 | SUCCESS |
| `freeze_default_noncopy_n1` | `freeze_default_noncopy-n01-u34` | `NonCopyByte` / Freeze | 128 / 139 / 140 | SUCCESS |
| `freeze_default_noncopy_n2` | `freeze_default_noncopy-n23-u34` | `NonCopyByte` / Freeze | 128 / 139 / 140 | SUCCESS |
| `freeze_default_noncopy_n3` | `freeze_default_noncopy-n23-u34` | `NonCopyByte` / Freeze | 128 / 139 / 140 | SUCCESS |
| `stable_default_activation-legal` | `light-controls-u34` | `Cell<u8>` / Stable | 32 / 40 / 41 | SUCCESS |
| `stable_default_cell` | `cell-u34` | `Cell<u8>` / Stable | 32 / 40 / 41 | SUCCESS |
| `stable_freeze_activation-legal` | `light-controls-u34` | `u8` / Stable | 54 / 62 / 63 | SUCCESS |
| `stable_freeze_u8_n0` | `stable_freeze_u8-n01-u34` | `u8` / Stable | 54 / 62 / 63 | SUCCESS |
| `stable_freeze_u8_n1` | `stable_freeze_u8-n01-u34` | `u8` / Stable | 54 / 62 / 63 | SUCCESS |
| `stable_freeze_u8_n2` | `stable_freeze_u8-n23-u34` | `u8` / Stable | 54 / 62 / 63 | SUCCESS |
| `stable_freeze_u8_n3` | `stable_freeze_u8-n23-u34` | `u8` / Stable | 54 / 62 / 63 | SUCCESS |
| `unstable_default_cell` | `cell-u34` | `Cell<u8>` / Unstable | 84 / 91 / 92 | SUCCESS |
| `unstable_freeze_u8_n0` | `unstable_freeze_u8-n01-u34` | `u8` / Unstable | 102 / 109 / 110 | SUCCESS |
| `unstable_freeze_u8_n1` | `unstable_freeze_u8-n01-u34` | `u8` / Unstable | 102 / 109 / 110 | SUCCESS |
| `unstable_freeze_u8_n2` | `unstable_freeze_u8-n23-u34` | `u8` / Unstable | 102 / 109 / 110 | SUCCESS |
| `unstable_freeze_u8_n3` | `unstable_freeze_u8-n23-u34` | `u8` / Unstable | 102 / 109 / 110 | SUCCESS |

## Activation variants

The exact predeclared unified patches are read from the executed control Git
object and applied in memory with old/new hunk-coordinate and context checks.
The effective source must match the request and oracle hashes:

| Variant | Patch SHA256 | Effective smallsort.rs SHA256 | Sole expected failure |
|---|---|---|---|
| activation-default | `cee9e21c4b5015d6daf53c286f781602d0890e4ed23239f968d228088335dcc3` | `ad516502d4783df0379ea3f48805c408b5bcde3ec064432476610080e3ecd0bb` | Exact parent-check assertion at line 41, `S1_ATTACHMENT_DEFAULT` |
| activation-override | `6dcb40cc4118035de700f0988a6766c96aad8f4def76513f0f10f275d091c356` | `90f20bce619de5535e633fc97f4a9dfd46715dc48e54912f5d1c9029984b131f` | Exact parent-check assertion at line 63, `S1_ATTACHMENT_OVERRIDE` |

The production post expression is never used for mutant clause matching.
The exact predeclared property ID/class/status/description/file/line/source line
and source hash must agree, with no second FAILURE. Each legal companion has the
same harness and full target instance in the production namespace and its parent
ensures is SUCCESS. This establishes attachment detection at the chosen level,
not positive correctness of the deliberately false mutant clause. Mutant return
covers are not assigned positive credit; other cover/role gates are unchanged.

## Validation and limits

228 tests PASS: eight positive cases and 220 rejection/mutation cases. Of those,
176 test the contract-binding checker directly below outer digest and inventory
gates, across all six impls and both variants. They reject raw-symbol, full module
stem, trait/type/comparator, diagnostic text/status/site/location, missing or
duplicate diagnostics/ensures, changed clause, caller substitution, frame status
and allocation-status mutations. Remaining cases check group/harness/request,
source SHA/site/impl/cfg, native reference/content/manual-definition links,
missing/duplicate property inventory, partial/NOT_RUN/timeout/binary drift,
producer edges, variant/patch/effective source/oracle and legal-companion mismatch.
An unclosed row retains PENDING with its concrete missing edge.

This policy trusts the pinned stock compiler, macro/codegen/driver semantics,
retained structured projections and GNU c++filt 2.42 (binary hash in PFC.json).
No independent AST/MIR/DefId/property provenance, compiler correctness, allocation
owner trace, B1/B2 or full-domain theorem is established. Null compilation_id
remains null. This component does not discharge independent caller, U, success
role, cover or other admission-root obligations. Std/control/tool/policy/ledger
and historical accept/accept-v2 are unchanged. No local compiler/verifier,
CI/build, push, publication or raw archive/log read was performed.
