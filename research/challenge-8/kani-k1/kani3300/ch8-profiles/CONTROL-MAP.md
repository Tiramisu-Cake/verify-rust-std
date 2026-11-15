# Guard/control migration — no silent deletion

The canonical address predicate and its requires disappear only because no migrated wrapper
accepts a comparator argument. Supplying a different F to these APIs is impossible (wrong
arity/type); this is a source/type guarantee, not an executed Kani failure. Static contract
comparison permits removal of only that identity predicate, retaining all geometry/modifies/posts.

| Historical control / assertion | New guarantee or negative oracle |
|---|---|
| profile_canonical_comparator, canonical, canonical_guard; `canonical comparator required` | Callback-free signatures plus direct original adapter. Source/type exclusion replaces runtime address comparison. No fabricated canonical-guard property is expected. |
| profile_wrong_f_swap_rejected_u8 | Name retained. Real swap_profile<BadCmpU8> with always_true against lawful lt_u8 model; [0,2] violates transfer. Expected `bad-profile swap transfer rejected`. No stub. |
| profile_wrong_f_sort4_rejected_u64 | Name retained. Real sort4_profile<BadCmpU64>; [0,2,4,6], always_true vs lt_u64 model. Expected `bad-profile sort4 order rejected`. No stub. |
| profile_wrong_f_insert_rejected_u8 | Name retained. Real insert_tail_profile<BadCmpU8>, [0,4,2] satisfies sorted-prefix model. Expected `bad-profile insert order rejected`. No stub. |
| profile_wrong_f_merge_rejected_u8 | Name retained. Real merge_profile<BadRelationU8>; lawful lt_u8 callback, reversed model, singleton halves [0,2]. Expected `bad-relation merge order rejected`. No stub or abort cut; lawful callback ensures normal-return witness. |
| new profile_bad_relation_rejected_u8 | Direct bad cmp/model equality at [0,2]. Expected `bad comparator-model relation rejected`. Positive companions: all11 profile_relation_* roots. |
| forwarding_contracts::rejects_always_true | Name retained. Three real trait-entry calls with test-only always_true closures, same order/count checker as concrete wrappers. Expected all three branch-local `bad {stable,unstable,Freeze} adapter relation rejected`; preceding full-value checks must PASS. Each [0,2] witnesses inversion after normal return. The wrapper itself has no F argument. |
| old `invalid {stable,unstable,Freeze} comparator reaches guard` covers | Explicitly renamed to `bad {stable,unstable,Freeze} static adapter reached`; each must be SAT. No address guard remains. |
| profile_full_value_checker_rejects_payload_change_u8 | Retained; real sort4 uses typed LtU8 closure, flips bit0 after return. Order check PASS, `full-value checker detects payload corruption` FAIL. Probe remains independent. |
| forwarding_contracts::rejects_payload_corruption | Retained; real u8 entry uses typed byte_less closure. Before corruption order/count PASS; payload-key preservation PASS; `full-value checker rejects payload corruption` FAIL. |
| helper_contracts::rejects_swap_comparator_writing_outside_frame_u8 | Unchanged PFC effectful captured counter. Must fail actual generated modifies property; property identity to be bound in CI. This control is a separate helper FnMut instance, not a claimed new profile body. |

All11 relation positives compare actual P::cmp with the unchanged model_less over arbitrary
full inputs and check both models after the comparison. They preserve volatile adapters.
Five new summary consumers check their pure ordered/transfer/full-probe-count conclusions and
caller/source frames; each may use only its newly qualified same-head companion. No test-only
bad profile may appear under stub_verified or be admitted because another Profile passed.

The four historical wrong-F reached covers remain literal-compatible; other ordinary covers
remain unchanged. Wrong-F roots now have different property IDs/counts and real-body semantics.
Exactly four old requires failures is NOT an acceptance oracle. Every new named failure,
frame checker and payload checker needs completed property binding plus all required covers;
setup/Unsupported/timeout/unrelated failure is UNKNOWN/STOP, not DETECTED.
