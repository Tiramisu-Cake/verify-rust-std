# Exact two expectation corrections

Original expectations.patch SHA256 da87f8729e2b52eb4f3b6095cb105d10031ce70a2f18985ecccb24381d8e5415.
Checked against clean exact CC3 with git apply --check before applying; artifact
preserved. Only the two specified .expected files change. Rust input bytes and
all other old goldens remain identical to CC3; no generic FAILED golden.

Allowed coordinator log /root/kani3300-h1-ci/cc3-r1.log was read only at the
predeclared windows3380–3383/4301–4312 and4881–4885/5509–5522.
CI43453928092 reports:

- capture_reference_legal: std::cell::UnsafeCell::<MaybeUninit<u8>>::new.unsupported_construct.1,
  FAILURE at core/src/cell.rs2335:9; exact reason in patch is UnionAsField for
  UnsafeCell<MaybeUninit<u8>>. Summary1/255 failed,17 unreachable. Construction
  stops before useful closure execution. This is neither capture nor PFC credit.
- capture_union_reference: capture_union_reference::closure0.unsupported_construct.1,
  FAILURE at source42:18; exact reason is dereference on a union field. Summary
  1/224 failed,10 unreachable. Boundary at callback union-field access, not a
  successful reference-payload proof.

Each expected file retains Checking harness, exact Failed Checks reason,
VERIFICATION:- FAILED, and0 successful/1failed/1total summary. These are output
matching requirements, not the whole acceptance oracle. Coordinator CI must bind
failure ID/class/location/source/model and confirm the complete failure set is
exactly that single Unsupported with no extra failures. Missing or partial
inventories, crash, cap or a different failure class do not pass this boundary.
Simple ref/scalar positives and payload-hole negatives remain required, unchanged.
Historical CC3 Quick failures are unchanged; corrected future matching claims no
new Quick PASS, mode qualification or independent proof credit.
