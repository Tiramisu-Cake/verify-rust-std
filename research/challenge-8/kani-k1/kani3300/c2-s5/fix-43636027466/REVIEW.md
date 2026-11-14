# Static correction review

CI43636027466 establishes a missing local PFC prerequisite, not a changed native outcome.
check_crate_items in kani-compiler/src/kani_middle/mod.rs enumerates all HIR free items
and checks every stub_verified target against all proof_for_contract targets. Restore
that existing same-target full-domain SimpleCheck companion in each of the two crates.
Its body matches the existing independently run replace-simple-check.rs (only pure
cover hooks omitted). Original root, target, helpers, contracts and domain are unchanged.

Authorized exception: each affected file now declares two harnesses, but kani-flags
selects exactly one original root with --harness <root> --exact before --cbmc-args.
tools/compiletest/src/runtest.rs::run_kani forwards those flags. Compiler codegen_units.rs
::determine_targets retains only exact selected metadata; driver metadata.rs rechecks
exact filters. The companion satisfies crate validation without entering this oracle's
verification inventory. Separate replace-simple-check.rs still verifies the PFC behavior.
No claim that companion presence proves a contract is made.

Goldens are unchanged. Checking harness names the selected caller; consecutive SUMMARY
and **2of or **0of are anchored to its check summary (not cover summary), verdict and
Complete1total constrain single-root execution. Negative root/helpers have no covers.
No matcher/driver/compiler/production or global-check changes; no weakened oracle.

Four sensitivity patches retain their exact hashes and input hashes and all apply
checks pass; no patch bytes changed. Manifest already includes --force-rerun. Previous
CI mutation attempts were INVALID/skipped, not detection. New build/native runs NOT_RUN.
This localized repair restores a compile prerequisite and retains all existing checks;
static review and requested wrapper formatting only, no additional build/CI/review-agent.
