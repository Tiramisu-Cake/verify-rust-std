# SCRATCHGEOM pre-build packet

- Worktree: `/root/verify-rust-std-kani-scratchgeom`.
- Branch: `experiment/kani-k1-scratchgeom-20261104`; task commit: `104d5e5ec9`.
- Library commit: `d23737213c5605cc6815f611dc15ae6a7f4c1874`.
- Tooling base: `59893bff1f`; lane/runtime/workflow files unchanged.
- Request: `scratchgeom-20261104-01`; stable owner in request: `k1-merge`.
- Owner availability must hold at dispatch; no owner reservation or dispatch is claimed by this packet.
- Kind diagnostic, runner `gcb-e2-standard-4`, jobs 1, timeout 10 min/root.
- `controls: false`, `inventory: true`; ordinary inventory expected **207 = 202 + 5**.
- No experimental uninitialized-memory or value-validity flags are added: this is the ordinary CI profile.

| Root under `verify::scratchgeom` | N | Scratch length | Allocation |
| --- | ---: | ---: | --- |
| `stable_u64_min_scratch_n2` | 2 | 18 | Separate |
| `stable_u64_min_scratch_n8` | 8 | 24 | Separate |
| `stable_u64_min_scratch_n17` | 17 | 33 | Separate |
| `stable_u64_scratch40_n8` | 8 | 40 | Separate |
| `stable_u64_shared_min_scratch_n8` | 8 | 24 | One 32-element buffer, split at 8 |

Each root runs the real Stable Freeze trait entry with arbitrary u64 inputs and arbitrary comparator
answers; volatile reads keep both comparator arguments observable. The existing full-byte probe counts
complete, padding-free u64 values before and after normal return. Only `panic_on_ord_violation` is stubbed
to an abort cutoff; there are no verified-contract stubs or ordering assumptions and no unwinding claim.

The shared buffer starts as `[MaybeUninit<u64>; 32]`; `split_at_mut` separates its regions, then the
entire input prefix is initialized before the sole reference cast. SAFETY comments justify its lifetime,
layout, initialization and exclusivity. Assertions check same allocation and disjointness; separate
fixtures assert different allocations. Scratch itself is never read by the fixture or value oracle.

Every root expects two satisfied covers: Stable Freeze general-with-scratch dispatch beyond the early
return, and normal return after the value assertion. The Freeze bound and general threshold establish
the stable specialization; efficient-swap is an unstable-only selector and is not asserted false for u64.

Static checks passed: rustfmt (edition 2024, skip_children), whitespace, unchanged existing v7 files
except module registration, exact five-root/request binding, request validator, unchanged tooling.
The inventory count is a source expectation pending the supported cloud inventory, not a local Kani result.
The <=60 s/root estimate is qualitative (fixed N, one route, unrolled probe); N17 is the timing risk.
Only successful roots with both covers and measured <=60 s qualify as ordinary v8 candidates.
Optional N32 and shared N17 remain outside this packet to limit the unmeasured solver work.

Paid timeout: 5 * 10 + 30 = 80 min; reserve **$1.0800** at $0.0135/min, own cap **$1.40**.
Pre-build ledger: 223 builds, used $94.5240, unfinished reserved $2.2275; with this reserve $97.8315
is below project cap $118.96. Recheck budget and owner availability at dispatch after coordinator GO.
One build, no retry; a compile-error repair is allowed only if actual own spend plus its reserve <=$1.40.
Task window: main 150 min + closeout 30 min. No local cargo/rustc/Kani/CBMC was run.

After exact-packet coordinator GO: dispatch this branch through `tools/k1g.sh`, immediately register
`tools/k1g.sh watch BUILD` and end the turn. On wake, use bounded helper summary/inventory and tooling
binding, publish `RESULT-SCRATCHGEOM.md` (<=25 lines), then the required final review/completion markers.
