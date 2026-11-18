#!/usr/bin/env python3
import json
from pathlib import Path
H=Path(__file__).resolve().parent
p=json.loads((H/'PINS.json').read_text());s=p['source'];c=p['control']
pins=f'''96/96 actual final-object offline/static/synthetic tests passed.

Task taskcf40e805eb47a5f11efdf27a62b06caf2bc2adff; issued owner17:01.
Frozen review f5dd71722f82ac59e37152927a5f4dd9eee6ea1a.
Frozen package 4e2801660d89d75a1357a420c78cd435159c35b3 unchanged.

Source {s['sha']}
tree {s['tree']}
sole parent {s['parent']}
worktree {s['worktree']}
Control {c['sha']}
tree {c['tree']}
sole parent {c['parent']}
worktree {c['worktree']}
Request SHA256 {c['request_sha256']}
Workflow SHA256 {c['workflow_sha256']}
Stock {p['tool']['sha']}, tree {p['tool']['tree']}.
Checkout control/source/tool = 7/5/2. Full identities: PINS.json.
G0 package identity is the commit containing this immutable directory; reported in READY,
not embedded recursively. Entry G0 cf40e805eb47a5f11efdf27a62b06caf2bc2adff.
'''
limits='''Native compile, expansion, type/method/trait selection, MIR, Kani/CBMC/verifier,
full runner, CI and causal repair NOT_RUN. Actual R3 failing unit/body UNKNOWN.
Both general32 roots retain verified-original-sort8 same-cfg registration only;
qualification NOT_RUN. DIAGNOSTIC_ASSUMED unchanged. No independent B1/B2 credit;
closed proof obligations 0. Reference 29/29 +9/14 =38/43 and r0..r3 charged0 only;
no ledger, reservation, budget, push, issue, PR, publication, submit or cancellation.
Fast OFF per owner, current settings retained, no subagents.
'''
closure='''R14-01/P1 is repaired by importing the original grandparent sort4_stable.
The source delta from frozen r4 is exactly one replaced import line (1+/1-).
All production functions/contracts and copied operation tokens remain identical.
The finite import expectation changes; the len>=8 branch remains, independently
of the chosen input32. NAME-RESOLUTION-MAP.json records both exact sort4 identities.

R14-02/P2 is repaired in the shared resolver used by both ordinary and combined
PFC gates. Explicit aliases recursively resolve by full identity, including self
and module aliases; cycles, ambiguity and missing local targets reject. Unknown
Kani attributes and unsupported imported/reexported attribute identities fail
closed before discarding them. A finite inert-attribute policy also rejects unknown
unbound/qualified attributes. The frozen macro self-reexport remains supported.
The exact ordinary1/ordinary2 review discriminator is replayed on both gates:
contracted swap_if_less rejects and safe s2_swap_seam remains inventoried.
Only the two synthetic source-byte guard maps are removed for that replay.

The new lexical gate derives six new functions plus two body-changed callers from
the SHA-pinned r3 fixture. It inventories 77 static call occurrences across all
branches and all11 effective contexts, follows active ancestor/module declarations,
resolves imports and self/super/crate aliases, checks declaration visibility and
compares copied static-call bindings against original bodies after declared seam
renames. Local functions, lexical parameters/local callable values, public provider
reexports, explicit prelude size_of and the pinned Kani macro provider are distinguished.
Methods, assert macros and associated-type implementation dispatch have explicit
scope limits in the map. Unsupported body items, generic expressions and qualified
type paths reject. This is a finite lexical source check, not Rust typing.

The gate runs unconditionally from s2_policy.validate_source before ordinary/PFC,
through actual runner.py check-source before stock setup/build. All11 rows share
exact pinned cfg. Required frozen-r4 rejection/fixed acceptance, removed/renamed/
wrong-target/cfg-disabled imports, foreign basename/visibility, module cfg,
qualified paths, aliases and callable scopes have semantic discriminators.
No algorithm/model/domain/frame/init/oracle changes; 11 roots/20 covers/6 negatives
and all caps remain. Protected collector/packer/diagnostic/error/B-01/B-02 controls
and workflow are byte-identical to frozen r4; runner changes only its two source pins.
'''
(H/'FINDING-CLOSURE.md').write_text('# Repair submitted for SAME14 closure\n\n'+closure+'\nEvidence: FINDING-CLOSURE.json, NAME-RESOLUTION-MAP.json, TARGETED-TESTS.txt,\nTEST-PROVENANCE.json, VALIDATION.json and full inventories/patch replays.\nAuthor repair status FIXED_FOR_REVIEW; independent APPROVE/CLOSED is pending.\n\n'+limits)
(H/'REVIEW14-REQUEST.md').write_text('# SAME Independent14 — delta review request\n\n'+pins+'\nReview only this immutable repair delta against frozen r4 and your frozen findings.\nSource/control delta patches, parent/full baseline patches and FULL-INVENTORIES.json\nare exact-object artifacts. Frozen originals and review outputs remain untouched.\n\n'+closure+'\nPlease adjudicate R14-01 and R14-02 closure and the new lexical gate scope/coverage.\nNo GO-request follows until SAME14 returns APPROVE/CLOSED. This file is a local\nrouting artifact; no external message, source publication or CI was performed.\n\n'+limits)
(H/'HANDOFF.md').write_text('# READY — SAME14 delta review\n\n'+pins+'\n'+closure+'\nFinal committed-object tests are in TEST-PROVENANCE.json/TARGETED-TESTS.txt.\nActual check-source gate trace, six exact patch replays and real shallow7/5/2\nchecks are in VALIDATION.json. Independent review is pending; no GO authorized.\n\n'+limits)
(H/'STATUS.md').write_text('READY_FOR_SAME14_DELTA_REVIEW. R14-01/R14-02 fixed for review; full pins PINS.json.\nNative compile/causal repair NOT_RUN, actual R3 failing unit/body UNKNOWN.\n')
(H/'VALIDATION.md').write_text('# Offline validation scope\n\nActual final-object source/control/request/workflow tests: TEST-PROVENANCE.json.\nExact review alias replay and name mutations: FINDING-CLOSURE.json.\nActual prebuild check-source, three-gate ALL11 trace, six exact patch replays,\nPython AST, payload/fixture/hash inventory and real shallow7/5/2: VALIDATION.json.\nFull relative inventories and frozen-package preservation: FULL-INVENTORIES.json.\nPrecursor trials found assembly/hash/sentinel issues and are not acceptance evidence;\nthe actual final transcript is bound to the exact final objects without substitution.\n\n'+limits)
print('Local SAME14 request, finding closure and handoff written')
