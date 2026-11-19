APPROVE — exact S4P2 offline executable package; zero blocking findings.

W14 reviews author g0 `90d861e59f996d35b23a5cb843e311b29efdabf7` under task
`bf3aba53618b759a11d3ff277e88ba66530ec708`, explicitly issued by user13:05 /new14.
This decision covers the committed package and exact identities below. It permits
root's final recheck and GO request only. Publication, executable GO, final run
binding, dispatch and accounting remain separate coordinator actions.

| Object | Exact identity |
| --- | --- |
| Source | `c12867b1e651a3927cbd9f169fe2c3d3728a44c3` |
| Source tree / sole parent | `47cca4ee5946b9ab543ea08cba7979cb1d21c4af` / `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` |
| Control | `4059c900e50ba179d824a1e6f6bd7798cf343e36` |
| Control tree / sole parent | `48c726afdc23886e43b36b3cb10f3c077f38e556` / `9e14e033f9ee31522b571c127609dcdff76d230b` |
| Stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| Tool tree / sole parent | `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` / `3e095c22a231de1d7acd2410b71f0fc8e6970c19` |
| Request SHA256 | `c6abee25796842b0a1af44009921045c3da82b36e0fead42a342e7c5d8e74969` |
| Workflow SHA256 | `4500edba80fbb48258c5b0a29c4d73a97fbb37fb26017da9f8251c147f30bd7f` |

Independent hash/identity checks cover the entire author packet (92 files,
91 manifest hashes), all137 control payload hashes, clean source/control/tool
HEADs, exact trees and sole parents. Each of six full patches was applied to a
temporary index with temporary object storage; every resulting tree matches the
actual pinned tree. These checks neither alter source worktrees nor rely on
author replay status strings. `IDENTITIES.json` and `PATCH-REPLAYS.json` retain
the results. The plan review's ROLE-SAT-CONTRACT and IMPLEMENTATION-GATES were
compared byte-for-byte with commit `e287943e116a102d5950295b2629d80a62d1f922`.

The source delta from accepted985062e contains exactly the new117-line module
`sorting_s4_network_partition.rs` and a guarded append to `verify.rs`; the old
verify file is an exact byte prefix. All other tree entries, production code,
contracts, models and old harness bytes remain identical. Reading the actual
kernel at smallsort.rs:332 establishes the relevant control flow: N0/1 returns
before scratch setup; N2/3/4 has no_merge=true, selects presorted_len=1, and
calls insertion_sort_shift_left with1/2/3 tail insertions. No network sort9/13,
sort4 or swap replacement is substituted for this path. Initialization of the
backing array is a harness premise, with no general initialization theorem.

Execution order is the four fixed negative controls checker_order_corrupt,
checker_count_corrupt, sort13_weak and s4p_cell_count_corrupt, followed by actual
network n2, n3, n4, N0..1. Every request row and source binding is Original/null.
The three S2 negative labels retain intended FAILURE; sort13_weak retains its
fixed descending [12..0] input and weak checker scope. The Cell checker alone
retains active SUCCESS and count FAILURE on [0,1]->[0,0], where order stays true;
it does not call a sorting callee or acquire a Cell provider qualification.

Each positive chooses all34 independent fullu8 bytes, uses allocation34/base1,
and calls the actual small_sort_network on [1,1+n). The exact u8/KeyLess
specializations enable the concrete value model and pointer-span predicates.
The unchanged model snapshots values, checks sortedness and full multiplicity
for every input value, and rejects invalid/length-mismatched snapshots. Equal
length and preserved multiplicities leave no room for a novel output value.
Every index outside the active span is checked, together with an arbitrary
outside canary. Assumptions constrain only the selected length and outside
canary; they impose no ordering or few-key restriction. Unwind36 is a proposal
whose native sufficiency remains unobserved.

Four literal SUCCESS assertion roles remain on each positive. The declared
cover sets in execution order have6/6/6/3 sites,21 total. Nontrivial roots keep
length, unsorted, duplicate, nonconstant output, descending-at-exact-N and useful
return witnesses. N0..1 has only N00/N01/return covers and four exact-bound
structural N/A metadata entries. The request binds labels, predicates, source
file/line/hash, class, status, domain, type and cfg. s4p2_policy.py:26 compares
the sealed inventory, then enforces the role contract; validate_roles:113 checks
actual source locations and complete literal site order. expected_observation:135
requires all declared covers SATISFIED, exact cover cardinality, located roles,
producer count consistency, and no unsupported guards, U, extra failures or
unknown statuses. Loop instances may multiply a source assertion only when all
instances match its class/location/status; producer IDs are never predicted.
The synthetic mutation tests passed. Source21 assertions/21 covers establish no
native property count or native SAT result.

The existing public prebuild entry runner.verify_source(...,prebuild=True) was
executed independently on the actual pinned source/tool exactly once, with no
lexer or report cache. All four maps were captured in this review directory.
The new module is present in ordinary, cfg/PFC, contract-stack and lexical maps.
The new contract-stack power set derives from all six actual cfg keys:64 unique
contexts,32 retaining the old controls-off subspace,32 sorting-enabled and8
ACTIVE normalization contexts. All projected function sets are nonempty. Static
inspection of s4p2_contract_stacks.py:98 and the selected ProjectionTests confirms
the full declarations and semantic clauses are compared, including effective
wrapper-to-direct normalization; no empty-projection equivalence is used.
New cfg and lexical readers require actual module registrations, active ancestry,
import/alias resolution and local callable checking. Ordinary stubs in the new
module are forbidden. Exact source hashes additionally bind the complete bodies.

The shared runner, check_package and collect changes relative to accepted2db
are restricted to explicit new-profile dispatch, request-derived identity/cfg
selection and explicit null targets on the new worker row path. The inherited
protected evidence, snapshots, process supervision, diagnostic capture, binding
metadata and old profile/lexer files are byte-preserved. In the new campaign,
source/tool paths are canonical before E0; request, source, control and binary
identities bind pre/worker/post snapshots. root_outcome:186 checks protected
evidence and compile provenance before accepting any worker state. Observed
errors/drift remain global stops for COMPLETE, FAILED and interrupted states.
Absent inner AFTER can use recovery only for verified interruption/cleanup and
valid controller post; present malformed/error values cannot be erased.

PID/start-time ownership, exclusive subreaper admission, pidfd identity checks,
escaped-group rejection, adopted-child reap, orphan-survivor rejection and
try/finally cleanup remain inherited unchanged. Original exits, signals, errno
and exception records remain available. Local timeout/failed observations can
continue serially as UNKNOWN; identity or supervision faults stop subsequent
roots. Deadline reserve and durable slot publication remain enforced. The new
Original/null checks cover worker, finalized terminal, sealed row and worker-row
replay paths. Native execution and telemetry in service fixtures are synthetic.

The local and compact upload-only readers first validate the trusted
request-derived terminal schema and genuine int8 selected_roots, before calling
legacy_collect (s4p2_campaign.py:350). They subsequently enforce terminal
state/reason consistency, selected order, completed prefix, seals, provenance,
fresh namespace, exact singleton argv/config/start, compile receipt and native
export binding. Seals cover structured evidence without requiring raw streams;
atomic fsync/replace publication and exact prefix preservation remain intact.
Independent selected tests passed both routes for full, stopped0/partial0,
all prefix lengths0..8, malformed schemas, recorded drift and valid interruption.

AUTHOR-FALLBACK-EMPTY-OBJECT is independently CLOSED on final4059c900.
The reviewer loaded the campaign code directly from true precursor
`321c266daf58309ae3eadc6d5c3f358766938ac0` and from the final object. A present{}
is incorrectly replaced by the precursor; final rejects it and preserves exact
bytes. Missing terminal still produces a valid stopped8-root fallback. Both
objects also reject the tested malformed schema values. Only the campaign's
presence test, its distinguishing regression, and the request's two payload
digests differ between objects. `FALLBACK-DIFFERENTIAL.json` retains14 cases.
No precursor result has been relabelled or rewritten.

The actual final workflow Validate receipt binds final4059c900, its tree, exact
request, workflow, script and stdout/stderr hashes. The workflow command is
check_package control followed by s4p2_validate.py. Suite selection retains
136legacy+56S3+35S32+40bridge+38S4P1+39S4P2=344 passing tests, exit0,
679.1141679468565s, margin1.5903069777871495 at unchanged18min. The exact
39 new cases are selected by s4p2_validate.NEW; the legacy suite bodies and
profile schemas/counts remain preserved. Validate-only full-text lexer caching
returns fresh lists and restores patched functions through ExitStack even on
exceptions; it is absent from production prebuild/runtime and caches no gate
result or source read. The321 precursor's727.578s/1.484 margin failure stays on
its own object. The reviewer ran no additional full Validate. The separate10
selected reviewer tests passed in56.178s; they are additional synthetic checks,
and the344-run receipt remains author-observed evidence with verified integrity.

Caps remain child600 includingcompile180, slot720, controller180, cleanup240,
campaign6900, outer7500, step7560, phase8100, setup1800 and job180min. Local6GiB
is sampled ownedPGID RSS, outer12GiB is an owned-process census, reserve2GiB
available; Ceff=min(6,12,A-2). Outputs remain16MiB stdout/1MiB stderr/8MiB export/
256MiB artifact. Eight slots plus controller/cleanup=6180 is arithmetic only.
Required source/control/tool ancestors are reachable within5/7/2 checkout depths;
the author's actual shallow receipts are hash-bound and independently checked
against graph distances. Workflow keeps one job, no retry/cron/auto-dispatch,
the existing branch filter and intentional historical ch8-s3-2 artifact prefix.

Native counts/status/SAT, stock compile, unwind exhaustion, actual runtime/cost/
memory fit remain NOT_RUN. N>=5/9/13/16/32/general network, initialization,
provider/caller/type/ownership/panic/unwind/MIR/B1/B2 remain OPEN. No new qualified
leaf or proof obligation is closed. Old location admissions and investigation11
grant no new emitter/common-location rule. Before any future attempt, root must
recheck full pins/manifests/limits and issue its GO request; the user coordinator
must separately publish exact source and bind a NONSKIP SAME-TREE control sibling
with sole9e14 plus actual head/ref/run/ledger eligibility. Those future identities
are UNKNOWN. This review performed no native execution, CI, push, source edits,
ledger writes, subagents or model changes; instructed High/FastOFF is preserved.
