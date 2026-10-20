# Candidate5 — source declaration order and exact checked header

Defect/applicability: Build4 all compile milestones0, but Rust annotation parser
refused non-leading let_lft at verified/lib.rs296. let_lft is a ghost declaration,
not a ghost statement. Restore it first in the loop source block, followed by
the same checked invariant and dynamic prep. The admitted late relocation leaves
a Noop at that exact original declaration location. Reconstruction now recognizes
only State.r9_guard_return Some + late_callback Some + leading exact-location
Noop immediately followed by Pure Invariant; keeps the same Noop inside the
While LoopInv body. Other shapes unchanged; no other statements crossed.

Independent GPT-6 Luna HIGH /root/r10_review reviewed actual diff: GO. Both
plan guards, exact source location, adjacency, preserved placeholder and existing
While invariant extraction verified. OCaml patterns/type fields checked statically;
no local compiler/verifier. Source/runtime identity and assembly/error anchors:
3 synthetic service tests PASS. Static cumulative source preflight required.
No ownership, assumption, model, runtime CFG, checker or posts changed.

Next attempt: compile + actual checked invariant + retained matrix in sameBuild.
Ceiling3600; accounted4=2288/execution2285, remaining1312. Timeout1200/reserve1260
fits. Observed full cold599/621/644; enough target+package margin, no separate
cold compile-only run. Main deadline23:48:01Z unchanged. Static/service GO is not
entry/backedge/exit evidence or proof credit.
