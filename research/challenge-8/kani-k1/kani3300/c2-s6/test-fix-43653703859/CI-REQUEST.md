# Test-only correction — coordinator targeted rerun pending

Candidate `503d7f0b1f23616f671cc69dc7b376703bb0af31`, tree `1905c29c46944e4cd075a65275509473cf8e80fe`; hashes: RESULT.json. Parent61eb; production/tree outside the two fixture
directories unchanged. No worker build/push/CI. Use existing targeted infrastructure,
unchanged tools/pins/checks/object-bits12. First fmt and all8 corrected fixtures with
actual --force-rerun; no --fix-expected/bless. Copy .rs now uses source,source plain
Copy operands. Confirm actual MIR same source place, Copy to both distinct arg indices,
initialized source-preservation companions N0. Copy-hole expected N2 raw-pointee/payload
pair is SOURCE-DERIVED, not observed on the fixed syntax; record actual native outcome.
Padded source unchanged; corrected goldens replay against original stdout but still
require actual new-head native matcher qualification. Require useful own successes,
exact N2 intended pair for holes, N0 initialized, one selected root and no extra failure.

Parent CI43653703859 reports all9 marker controls, units/kani/ui/script/json and4/4 S5
mutations pass/detected; matched observations establish hook predicate change. Preserve
that coverage distinction and original receipt identities. No production delta or new
hook observation source. Original bounded qualification scope remains; no local builds,
full regression/new workflow, Gate A3-platform or SEL1 replay authorized in this fix.
Unexpected control/failure => preserve exact repro, no arbitrary count blessing.
