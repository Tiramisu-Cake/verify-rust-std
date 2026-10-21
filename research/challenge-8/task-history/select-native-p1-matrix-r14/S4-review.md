# R14 S4 independent review

## Result

GO for the reviewed localized redirect-binding fix and compact-transport ordering change. This is source/test review only; it is not Build evidence or proof credit. No actual toolchain or Cloud Build was invoked.

## Reviewed source identities

- `research/challenge-8/cloud-build/sort4-caller-entry-native/a1-runner.py` SHA-256 `b55f3049f10fc551a1fec1b3f72ec7219d0240366bc37e2e89435709510c0411`
- `research/challenge-8/cloud-build/sort4-caller-entry-native/test_a1_redirect_control_binding.py` SHA-256 `aea4499c766a568f7483f147d632e37381e4897805f101f493c279ac5e21ddd3`
- `research/challenge-8/cloud-build/source-input.py` SHA-256 `2da52a29cf4144d0b85f054d154f775b27a1d9d72a47460b82d415fbb531662b`

## Findings

The negative N-clause redirect can now retain a source identity on a pre-AST partial only after `_source_case_input_identity` binds raw source/unit IDs and certificate hash to the constructor package and current verified/original fixture bytes, including the expected ghost-stripped relation. Checked-helper record validation still precedes the partial return. The eventual redirect classification separately requires the exact prepared control document/hash, current source pair, same-Build/profile caller environment with the forced redirect, fresh evidence root, terminal integer exit 2, matching log digest, and the exact intended first refusal diagnostic. Missing or mismatched identity remains inconclusive and cannot reach the matrix gate.

The compact source encoder changes only the ordering of the compact recipe’s shared-object pool, using deterministic `(type, -size, oid)` ordering. Legacy order remains unchanged. Decoding indexes the pool by OID and checks both the referenced pool set and each restored Git object identity, so order does not alter source closure or selected paths. No object, recipe input, codec, decoder limit, or runtime/tool semantic was changed.

Focused synthetic validation: `python -m unittest test_a1_redirect_control_binding -v` passed 7/7. The runner/classifier/context integration set `python -m unittest test_a1_redirect_control_binding test_a1_matrix_classifier test_a1_runner_lifecycle test_a1_runner_context -v` passed 32/32. Existing transport validation: `python -m unittest test_source_input_transport -v` passed 6/6, including compact restore/closure, legacy compatibility, corrupt identity/size, ambiguous fields, codec rejection, and truncation controls.

The changed runner must be included in the active profile/helper pin refresh before a subsequent Build. The transport-order change’s measured archive improvement is a packaging/transport observation only; it does not establish verifier acceptance.
