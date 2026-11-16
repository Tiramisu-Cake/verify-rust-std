# S1-04 checkout depth audit

Frozen production graph: new control → `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`
→ tool `0aac16ef62da9e9d5645782d458593e5d78143ba`. Depth **3** is the exact
sufficient depth: both endpoint commits and their trees are present; no merge-base or
history walk beyond tool is used. Depth2 lacks the tool endpoint. Full history (0)
would also work, but fetches unnecessary upstream history. The graph is asserted by
`depth-fix/validate.py`; the YAML gate freezes all12 depths. Any parent/pin change
requires a new graph audit and shallow regression.

| Checkout, all4 jobs | Git operations in CI preflight | History requirement | Depth |
| --- | --- | --- | --- |
| control | `rev-parse HEAD`, `HEAD^`; `rev-list --parents -n 1 HEAD`; `status --porcelain --untracked-files=no`; `diff --name-only <tool_sha> HEAD`; `ls-tree -r --name-only HEAD .github/workflows` | HEAD, immediate parent, tool endpoint (grandparent) | 3 |
| export | `runner.verify_source`: `rev-parse HEAD`, `HEAD^{tree}`; `cat-file -t <std_sha>`; `status --porcelain=v1` | HEAD and its tree only | 2 unchanged |
| tool | same four `verify_source` operations, with tool pin | HEAD and its tree only | 2 unchanged |

`check_package.control` repeats `rev-parse HEAD` for its result. `build` and
`fallback` contain no Git commands. All `git(...)` calls in `runner.py` are covered
by the identity checks above and overlay `status --porcelain=v1 -z`. Overlay
`git apply --check`, `apply`, reverse `--check` and reverse apply use working-tree
files/index, not ancestors. Tool setup additionally uses `git config --global --add
safe.directory` and `submodule update --init --depth 1`; submodule commits come
from the pinned HEAD tree and are fetched separately, not from tool ancestry.
No setup, submodule update or compiler was run locally.

The existing g0 `s1-04/validate.py` is an offline preparation validator, **not a CI
step**. Its std `rev-parse HEAD`, `HEAD^{tree}`, status and control HEAD reads are
HEAD-only. Its `diff f22f84f316... HEAD` requires the S′ commit two edges behind
std HEAD (`5be85699... → 9f9622b0... → f22f84f3...`), hence depth3 or a full local
repo. That comparison is absent from workflow/check-source; it does not justify
changing CI export depth2. `yaml-fix/validate.py` additionally compares/shows the
old sibling control `5fd53873...`; sibling commits are not reachable by any depth
of a single-branch clone of the new control. Those historical comparison commands
remain full-local-repository preparation checks, and are not copied into CI.
New `depth-fix/validate.py` likewise compares/shows old sibling `2a532e59...` locally;
its log/author, parent and current tree metadata reads fit current depth3.
No claim is made that a CI checkout can run historical g0 comparison validators.

`test_every_checkout_shallow_clone_runs_real_identity_operations` creates a tiny
real Git history with an extra older ancestor, then clones **each job's three
checkouts**, with `file://`, `--no-local`, `--single-branch` and the actual YAML
depths. It asserts actual shallow state, exact visible commit count and absence
of object alternates. It invokes real `control()` (including YAML, path inventory,
payload hashes and all Git operations) and real `verify_source()` using synthetic
pins. Extra current metadata reads also run on shallow control. A separate depth2
clone passes HEAD^ but fails the actual control diff with exit128; depth1 fails
HEAD^. Real production pins/hashes/anchors are checked separately on full local
repositories. No production shallow clone or GitHub run is claimed.

`test_checkout_depth_policy_in_every_job` mutates each of12 depths independently;
the gate rejects insufficient, zero/full-history and off-policy depths. Existing
native-type tests still reject strings, null, booleans/containers and negatives.
All previous wrapper/source/oracle/error-path tests remain present.
