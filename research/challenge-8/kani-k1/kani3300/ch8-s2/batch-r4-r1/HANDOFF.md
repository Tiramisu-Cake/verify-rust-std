# READY — SAME14 delta review

96/96 actual final-object offline/static/synthetic tests passed.

Task taskcf40e805eb47a5f11efdf27a62b06caf2bc2adff; issued owner17:01.
Frozen review f5dd71722f82ac59e37152927a5f4dd9eee6ea1a.
Frozen package 4e2801660d89d75a1357a420c78cd435159c35b3 unchanged.

Source bd62e54df1b4749154790aa3db3cc7978f547f75
tree dc2e7a7f258719a05c65bbb9b1e2c7f1e8271ac8
sole parent 97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a
worktree /root/verify-rust-std-ch8-s2-r4-r1-w13
Control 0e8c836857344866564e1423ad5d8d28bbc4106b
tree 9f7c903f2039e6a52b19f37c5f32fbd9cc86566f
sole parent 9e14e033f9ee31522b571c127609dcdff76d230b
worktree /root/kani-ch8-s2-r4-r1-w13
Request SHA256 9d165365933b6bc117311d7d52568f834bc2f083c2272800803a84883f286717
Workflow SHA256 93521eefcbd83c50218d8484b2f8bbc044ff9acd2dd2b003749fe0e316c0ea6c
Stock 0aac16ef62da9e9d5645782d458593e5d78143ba, tree 9d8bc9312bf955ef126d32b819b3cd0ed105ed2b.
Checkout control/source/tool = 7/5/2. Full identities: PINS.json.
G0 package identity is the commit containing this immutable directory; reported in READY,
not embedded recursively. Entry G0 cf40e805eb47a5f11efdf27a62b06caf2bc2adff.

R14-01/P1 is repaired by importing the original grandparent sort4_stable.
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

Final committed-object tests are in TEST-PROVENANCE.json/TARGETED-TESTS.txt.
Actual check-source gate trace, six exact patch replays and real shallow7/5/2
checks are in VALIDATION.json. Independent review is pending; no GO authorized.

Native compile, expansion, type/method/trait selection, MIR, Kani/CBMC/verifier,
full runner, CI and causal repair NOT_RUN. Actual R3 failing unit/body UNKNOWN.
Both general32 roots retain verified-original-sort8 same-cfg registration only;
qualification NOT_RUN. DIAGNOSTIC_ASSUMED unchanged. No independent B1/B2 credit;
closed proof obligations 0. Reference 29/29 +9/14 =38/43 and r0..r3 charged0 only;
no ledger, reservation, budget, push, issue, PR, publication, submit or cancellation.
Fast OFF per owner, current settings retained, no subagents.
