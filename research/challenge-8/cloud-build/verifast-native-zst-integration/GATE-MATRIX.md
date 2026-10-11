# Merged candidate gate matrix — reviewed fresh evidence

Tool `46181aff379a5d4231cc51814cfe3732bda21c03`; profile `verifast-native-zst-c3-integration-20261011-h`; tested infra/proof `03c2f4e134473253045d716a9779cc1b8530d0bb`. Build `47ee47d9-274b-4b13-84e2-167ba88ff770` is the first fresh experiment. Raw evidence has been independently reviewed; the two C/C++ controls are independently reviewed from supplemental Build15f28723 on the identical binary. Historical Bool C3 READY and native evidence retain their previous pins.

| Required gate | Current result | Evidence/credit boundary |
|---|---|---|
| Full 30-module pack, two XZ, Python imports/all fixtures before expensive build | REVIEWED_PASS | Actual Cloud imports, two XZ, 30 modules and all fixtures prepared successfully before compilation |
| One compiled effective tool, seven file pins, frozen kernel | REVIEWED_PASS | One compiled binary 6b73208f…; all seven pins match; frozen kernel verified |
| Native C1 positive and normal/unwind negatives/admission | REVIEWED_PASS | Existing exact C1 fixture and full paired MIR/refinement; added ZST guard domain only |
| Native C4 four actual callbacks, early returns, normal/unwind CURRENT closure | REVIEWED_PASS | Exact guarded four-call prefix; no native C4+select or caller theorem |
| Native C4 five false VCs plus source/body/malformed/mixed admission | REVIEWED_PASS | Refusals must precede admission; default-off frontend observation carries no semantic-negative credit |
| Rust ZST/non-ZST/layout/MaybeUninit and no-extra-permission matrix | REVIEWED_PASS | Nine source/refinement/model cases, exact four negative VCs |
| Preserved C nonempty/C++ empty positive-size controls | REVIEWED_PASS | Build15f28723 both exit0, one statement and successful linking with -shared, exact same sources/prepared/binary/sevenpins; not a complete C/C++ suite |
| Actual pointer selector, all nine bodies/helpers | REVIEWED_PASS | Fresh bodies and original posts; no assumed summary |
| Bounded C1→C4 and nine exact controls | REVIEWED_PASS | Nine fresh adapter rows reach their exact first VC; historical component rows remain archival |
| C4 plus first actual select, 466 statements, sealed typed AST transport | REVIEWED_PASS | Same invocation reproof and consumer; exact producer/location-only certificate required |
| FRAME/original pointer/thread/CURRENT, posts, source/contract/type/Move/edge | REVIEWED_PASS | Six intended VCs and exact admission stage; raw_ptr_own supplies no pointee permissions |
| Cleanup and reachable-unwind controls | REVIEWED_PASS | Requires exact reachability/VC/admission observation, not setup failure |
| Strict lifetime/pointer-value/ManuallyDrop retained fix | REVIEWED_PASS | All affected four/two/five fixtures forced fresh because verifast1 changed |
| Outer-F local Bool HRTB and normal/unwind closure | REVIEWED_PASS | Positive control; no cut106 rejection expectation |

Open, outside this candidate's readiness claim: actual caller/source correspondence of the added ZST guard; native C4+select composition; complete sort4/native caller; general O23 metadata escape and reference-output sketch OPEN/NOT_RUN; inherited experimental O26/A1/memory/prelude/compiler/supplied-entry assumptions; full upstream test suite and owner adoption. These are not automatically requirements to expand the exact Bool/native guarded fixture profile. They limit any later use to the declared domain. No automatic continuation or profile acceptance.

Read [native/C4 raw review](../../verifast-review/native-zst-20261011/RAW-NATIVE-REVIEW-47EE.md), [Rust ZST raw review](../../verifast-review/native-zst-20261011/RAW-ZST-REVIEW-47EE.md) and [Bool raw review](../../verifast-review/native-zst-20261011/RAW-BOOL-REVIEW-47EE.md). Positive rows and expected-VC/admission controls are distinguished in these reviews. REVIEWED_PASS in this compact matrix credits the intended gate, never a positive proof of a negative fixture. The diagnostic JSON flags and Cloud FAILURE are preserved unchanged.

[C/C++ affected-only raw review](../../verifast-review/native-zst-20261011/RAW-C-SUPPLEMENT-15F2.md) closes the two link-affected controls. **READY_FOR_INTEGRATION_REVIEW** for this exact fixture profile only. Both Cloud FAILURE statuses and unaccepted diagnostic summaries remain unchanged: primary failed the C/C++ link, supplemental deliberately stops after both proofs for raw review. This separate addressed assessment is not Cloud SUCCESS or owner adoption.
