# S3-2-r1: GO request for one bounded attempt

Status: **READY_FOR_DELEGATED_COORDINATOR_GO**. Root agrees to one eight-row
workflow attempt after the coordinator verifies the actual publication and trigger
bindings below. The coordinator owns dispatch and accounting.

Independent review `b5a0878d35b6a3de4e65ef68dbd86d711340e75a` approves exact package
`792ca31fa8e5e80380498d9903d9115cdae42d40`, with no blocking findings. Root verified
36 package files/35 hashes and seven review files/six hashes against committed
bytes, plus clean source/control/tool heads, trees and sole parents.

| Binding | Exact value |
|---|---|
| Source | `1b4a904f8144172f0a3682f84f1bd4afd80eaf5d` |
| Source tree | `ac51d04e17b4bf53db378889561d21399cc6782e` |
| Source sole parent | `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` |
| Stock Kani | `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| Reviewed control | `775574eb2f361ef90eade30330ff0d608530287f` |
| Required trigger tree | `ef1cf70982121cd1e212d4ddb324cc302d0ac219` |
| Required sole trigger parent | `9e14e033f9ee31522b571c127609dcdff76d230b` |
| Request SHA256 | `75603378a45639991f837ea1ea259f9a56cc452426c6f306cda6d53f5e51e47c` |
| Workflow SHA256 | `0fde14cf5513f81565bc2eea37864013e7d30f82dc3062788ba2fb34b575939f` |

Publish the exact source commit, or confirm that it is fetchable from
Tiramisu-Cake/verify-rust-std, before pushing the trigger. Create a nonskip
same-tree sibling of the reviewed control whose sole parent is9e14. Verify the
actual full SHA, tree, parent, range and skip directives:9e14..FINAL must contain
exactly one new nonskip commit and exclude the skipped candidate. Canonical
request/workflow bytes stay exact. Inherited accounting, control_reference and
repair fields are historical provenance; the current balances are stated below.

Use repository Tiramisu-Cake/kani, event push, a branch matching
`uninit-ci/ch8-s3-2-*`, workflow `.github/workflows/ch8-s2.yml`, job`s3_leaf` on
ubuntu-24.04. Verify required remote objects and checkout depths **control7,
source5, tool2**. Bind the actual source ref, trigger full SHA/ref and run/attempt
before reporting dispatch. One attempt is authorized; a further attempt needs a
separate review/GO decision. Keep automatic reruns disabled.

The fixed serial order is checker_order_corrupt, checker_count_corrupt,
sort13_weak, i_p01_b1_16, m8_s32_d00_allinit, i_p16_b1_16,
m8_s32_d00_partial_diag, m8_s40_d16_partial_diag. This is **three fixed negative
controls, three bounded actual-body PFC candidates and two partial diagnostics**.
The diagnostic category remains DIAGNOSTIC_ONLY_INITIALIZATION_OPEN: admissible
observations cover the full-byte functional result and actually checked known-value
frame. Actual initialization mask, destination initializedness and provider
eligibility remain OPEN even if native verification succeeds.

Preserve full u8/KeyLess values, reviewed geometry/frame/init construction, actual
callees, existing contracts and strict U/location/status/guard/role/cover/identity
gates. Introduce no ghost mask, vacuous init role, summary substitution or flag
change. The old f740 location case is limited to its original run. Maximum
prospective candidate coverage is32/256 original insertion pairs and1/1122
original allinit merge pair; all34 sort8 init/caller contexts and fullN16/N32,
type, odd-merge and locality goals remain OPEN. Qualified new leaves and proof
credit are zero before native results and separate admission.

Use one job with shared setup/tool build and eight fresh singleton invocations.
Caps remain child600s **including compile180s**, slot720s, local6GiB sampled
owned-PGID RSS, outer12GiB plus2GiB headroom, campaign6900s, outer7500s,
step7560s, phase8100s, setup1800s, job180min and Validate18min. The6180s slot envelope
is arithmetic, not a fit guarantee. Local continuation requires verified cleanup
and valid protected evidence; observed drift/read errors stop globally and retain
the completed prefix. RSS is sampled, not a strict kernel/cgroup/whole-tree peak.

Author final Validate:227 PASS once in569.679665s,1080s cap,1.895802x margin.
The reviewer audited receipts/code and passed562 independent static assertions
and six exact patch-tree replays. Native compilation, proof, cost and fit remain
NOT_RUN. The enabled-init method plan concerns future prerequisites and changes
neither this package nor its flags.

**Current accounting: item1 31/31, item2 12/17, total43/48.** A counted attempt
would produce **item2 13/17, total44/48**. Root changes no ledger, charge, refund,
reservation or capacity grant. This GO authorizes no item1/#4591 run or owner-only
PR/issue/comment/open-PR-branch publication. After dispatch, return exact run pins;
terminal bounded intake and case admission remain separate gates.
