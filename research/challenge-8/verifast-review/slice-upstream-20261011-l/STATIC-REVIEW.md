# Independent static review — Sol /root/slice_upstream_review_l

Reviewed base0a83 and candidate1ef8474610274bbf9d0652613ac2cabbb1fc476b. One-line exact arm agrees with pinned Rust method's runtime typed cast; no kernel/spec/memory/lifetime/resource change and no research dependencies. Normal in-out slice resources are retained by positive bodies. Empty/MU pointer equality covered in real calls.

Original negative in3f06 could fail merely because its array remained closed. Revised1ef847 opens array(mu, ...) before cast/dereference; marker is read line8. No further static blocker. Baseline auditor's substring check alone is insufficient because filename contains as_mut_ptr. Fresh raw baseline must report missing method; unmarked negative must fail at line8 with the intended initialized-byte chunk, after open-array success. Static GO is not proof or upstream acceptance. Fresh evidence independent review pending.

## Corrected negative registration review

Independent reviewer found that mysh runs ordinary commands through /bin/sh, so Bash [[...]] is unsuitable there; use POSIX case. It also traced reportShouldFail in src/verifast1.ml: a //~ directive is not inert without allow_should_fail; remove it for the unmarked diagnostic. Final095ef553 has both fixes. Static GO from reviewer for second Cloud Build, not readiness/proof. Runner requires target line8 heap-chunk error; v2 auditor additionally requires the exact baseline missing method message. No proof check suppression flags introduced. Baseline build now asserts source/bin matches base exactly (candidate test/metadata Git head retained).
