# #752 native binding check

**Use one targeted Ubuntu job in the existing fork Actions control lane.** Run `45018616243/1` already passed organizer acceptance with 16/16 jobs, 245 SmallSort roots per platform and a 79-minute longest shard. Repeating `kani.yml` costs another full matrix and still gives terse output with controls off. A targeted job can collect regular properties, stock export and the small native binding projection in one setup. Reusing the fork supervisor gives an enforced 8 GiB child cap and consumes one fork slot with zero GCB spend. [Accepted run](RUN-45018616243-SUMMARY.md) · [Worker task](BINDING-CHECK-IMPL-TASK.md)

`k1g.sh` can reserve a standard-4 diagnostic build. The comparable 13 × 5 min request plus 30 min overhead reserves 95 min, or **$1.2825** at the repository script's $0.0135/min rate. Its stock GCB path provides a machine memory limit and RSS sampling. The mixed cfgs, enforced child cap and native projection require control work. The $118.96 project ledger in the helper is distinct from the applicable item-2 GCB ceiling. Before any GCB alternative, the coordinator must establish that ceiling, current spend and reservations, and confirm Brief access to the projected members. Use no GCB reservation for this plan. [GCB accounting](../tools/k1g.sh) · [GCB runner](../tools/gcb-k1.sh)

## Frozen invocation

Candidate `152f11556ab19c6dcfa21b5a0f1096603530ce67`, tree `08c6c08235035dbca44715c4b4822f5c34c041f6`, parent `5402b33188d51d4c30e1302af710a27c7a60d831`. Tool `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`, stock dependencies from that pin, including CBMC 6.11.0. Build the tool once. Use separate exact invocations and fresh target, output and export paths under the runner temp directory. Preserve candidate and tool source trees. [Source and fixtures](IMPL-HANDOFF.md)

```bash
"$KANI/scripts/kani" verify-std -Z unstable-options -Z function-contracts -Z mem-predicates \
  -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing --no-assert-contracts \
  --harness "$selector" --exact --jobs=1 --output-format=regular --harness-timeout 240s \
  -Z export-json --export-json "$root_export" --verbose --keep-temps \
  --target-dir "$root_target" "$STD/library" --cbmc-args --object-bits 12
```

Use the stock solver (CaDiCaL) and normal organizer checks, with uninit/value-validity OFF. Unwind resolves to 32 from each root's attribute. Remove inherited `RUSTFLAGS` and `CARGO_ENCODED_RUSTFLAGS`. For the five opt-in roots only, set `RUSTFLAGS='--cfg kani_smallsort_controls'`. Preserve assertion reachability and unwinding assertions. Record actual argv and effective values. `--no-assert-contracts` keeps unrelated methods in Original. Explicit Check and Replace retain precedence.

## Exact roots and expected outcomes

Prefix every selector with `slice::sort::shared::smallsort::verify::trait_contracts::`. All 13 roots already exist in the frozen candidate. The five supporting ordinary roots bind the two Freeze providers and all three callers to the precise summary. The other Stable specialized cases stay covered by the accepted organizer run. In the tables, attribute lines refer to `smallsort.rs` and named fixture checks refer to `trait_contracts.rs`. [Exact root and control anchors](IMPL-HANDOFF.md#ordinary-roots-и-ожидаемое-evidence)

| Root | Exact selector suffix | Required native result and role |
| --- | --- | --- |
| D-S | `stable_default_sorts_permutation_cell_u8_backing4` | SUCCESS. Own Stable `Cell<u8>` default post, attr 40–47. `outside slice unchanged` and `stable scratch sentinel unchanged` SUCCESS. Actual insertion |
| D-U | `unstable_default_sorts_permutation_cell_u8_backing4` | SUCCESS. Own Unstable `Cell<u8>` default post, attr 102–109. Outside frame SUCCESS. Actual fallback |
| D-F | `freeze_default_sorts_permutation_noncopy_u8_backing4` | SUCCESS. Own Freeze `NonCopyKey` default post, attr 162–169. Outside frame SUCCESS. Actual general with private scratch |
| F2 | `freeze_sorts_permutation_u64_backing4` | SUCCESS. Actual Freeze Copy `u64` N2 Check, own post at attr 204–211 and outside frame SUCCESS |
| F3 | `freeze_sorts_permutation_u64_backing5` | SUCCESS. Actual Freeze Copy `u64` N3 Check, same clause and outside frame SUCCESS |
| U2 | `unstable_sorts_permutation_u64_backing4` | SUCCESS. Own Unstable Freeze post at attr 126–133 and outside frame SUCCESS. Freeze Copy N2 Replace linked to F2 |
| U3 | `unstable_sorts_permutation_u64_backing5` | SUCCESS. Own Unstable Freeze post at attr 126–133 and outside frame SUCCESS. Freeze Copy N3 Replace linked to F3 |
| C3 | `verified_forwarding_sorts_permutation_u64_backing5` | SUCCESS. Plain Unstable forwarding to the F3 Replace. `forwarded output is sorted`, `forwarded output preserves full multiplicities`, and outside frame SUCCESS |

For each ordinary root, require the `sort model enabled before call` assertion and all mandatory generated checks to be SUCCESS. The five covers must be SATISFIED: `sort model enabled before call`, `ascending input returns`, `descending input returns`, `duplicate input returns`, `trait small_sort returns`. For each Check, bind the named post to the generated `assertion` for that root's actual `ensures`, with exact ID/class/description/location determined from native output. Check lowering includes the DFCC write set on active `v`, body safety and effective unwind checks. [Bodies](/root/verify-rust-std-pr752-trait-contracts/library/core/src/slice/sort/shared/smallsort.rs:39) · [Fixtures](/root/verify-rust-std-pr752-trait-contracts/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:16)

| Root | Exact selector suffix | Expected assertion at `trait_contracts.rs` and cover |
| --- | --- | --- |
| K1 | `rejects_high_bit_corruption_u64_len3` | Sole `assertion` FAILURE `high-bit corruption preserves sorted full values` (234–237). `unchanged sorted snapshot passes checker` SUCCESS. `sorted high-bit corruption reached` SATISFIED |
| K2 | `rejects_changed_multiplicities_u64_len3` | Sole `assertion` FAILURE `same set preserves full multiplicities` (254–257). `sorted multiplicity corruption reached` SATISFIED |
| K3 | `rejects_reverse_pointer_sorted_u64_backing5` | Sole `assertion` FAILURE `reverse pointer output is sorted` (280). Reverse-pointer guard off and outside frame SUCCESS. `guard-disabled reverse pointer can return unsorted` SATISFIED |
| K4 | `rejects_function_item_sorted_u64_backing5` | Sole `assertion` FAILURE `function item output is sorted` (315). Function-item guard off and outside frame SUCCESS. `guard-disabled function item can return unsorted` SATISFIED |
| W1 | `freeze_frame_function_item_u64_backing5` | SUCCESS. Actual Freeze Copy Check with function-item `F`, guard-off assertion, DFCC and frame SUCCESS. `descending input returns`, `non-descending input returns`, `trait small_sort returns` SATISFIED. Frame scope only |

## Resource envelope

One fork job, `ubuntu-24.04`, serial roots. Per root 300 s wall including compile, verification and native projection. Child PGID RSS cap 8,388,608 KiB, outer cap 12,582,912 KiB, reserve 2,097,152 KiB. Record effective cap as limited by the runner's available-memory guard. Job ceiling 105 min = up to 30 min setup + 65 min child windows + 9 min finalization + 1 min margin. Refuse new roots inside the final 330 s of the verification window. Historical **native VT** plus the default estimates suggests 7–10 min aggregate across these roots. Std setup, per-root compile and evidence collection are additional wall time. No automatic retry. [G3 measurements](/root/verify-rust-std-kani3300-gateb-prime/research/challenge-8/kani-k1/RESULT-TRAITPFC-G3.md)

## Offline acceptance

1. Verify run/attempt, frozen control/request and source/tool SHA and trees, dependencies, generated input hashes, actual selector and cfg, OB12, unwind 32, cap/reap and terminal exit. Require one matching harness per invocation. Read structured evidence through the coordinator-approved scoped channel identified in GO. For any GCB run use `smallsort-brief <build-uuid>`. Report unavailable members and keep their roles `UNKNOWN` if authorized scoped projections are unavailable.
2. Reconcile each complete regular `RESULTS`/`SUMMARY` projection with stock export and exit, including successful, failed, unreachable and cover records. Stock export contains check totals and failure/cover summaries. Use regular records for individual SUCCESS cases. Preserve native ordinal, ID, class, status, full description and Location (retain absent fields explicitly). Drift, lost records, timeout, cap, unsupported/error results and unresolved required reachability are open findings. Any unrelated UNREACHABLE row needs a source guard. Grouped IDs can cover repeated executions with exact source role, terminal SUCCESS, successful unwinding and a reached return, per the existing rule. [Grouped-property rule](../item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md#правило-допуска)
3. For each D Check join `attributes.kind.target_fn`, the nonempty compiled `contract.contracted_function_name`, actual `goto-instrument --enforce-contract` and native `ensures` / DFCC properties to the exact default impl and `F`. Tie the selector and prepared GOTO inspected to the same solver invocation. Confirm the pre-state `old` guard/snapshot on initialized input, actual algorithm in the Check, `modifies(v)` and the per-root frame assertions. Stable default observes the initialized scratch sentinel. A required native post with ambiguous provenance stays open even with five covers.
4. For F2/F3 and U2/U3 confirm the same native Check roles for the exact full-width `u64` fixtures. For U2/U3 and C3 join `verified_stubs` and the reachable native call path from real Unstable to the matching Freeze Copy Replace. Tie `old` before havoc, writes to active `v`, and the conditional post `ASSUME` after havoc to the same clause and comparator. A Replace `ensures` is an assumption in the generated path. Its relevant SUCCESS properties belong to the caller and its separately checked provider. In K3/K4 bind the same replacement mode with the guard disabled for their exact `F` and value. These are sensitivity controls. [Check macro](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/check.rs:24) · [Replace macro](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/replace.rs:101)
5. Record separate verdicts for the three default bindings, both providers, each consumer and each opt-in control. Freeze the root → native symbol → source-clause → property record with evidence coordinates. Preserve run 45018616243's matrix acceptance and the bounded normal-return scope. Outside-type or general proof credit and the PR update are separate.
