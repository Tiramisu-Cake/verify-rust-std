# CC1 — cycle containment only

Worker14, 2026-11-13. Base C2 fef9e0f38c0c645027f20223a562c7008969d9a9.
No CC2/CC3, SCC support, runtime model, runner, solver or check-policy changes.

## Identity and applicability

The MIR solver already computes an intraprocedural fixed point. Its regular-call
callback synchronously invokes another solver; that interprocedural recursion had
no guard. `AnalysisKey` contains rustc's exact `Instance` (instance kind plus
monomorphized generic arguments) and whether the selected body is overridden.
One immutable override map is borrowed for the entire root: for each Instance it
contains exactly one emitted registration/discarded body. Therefore `(Instance,
overridden)` uniquely identifies the selected body within this context. The key
does not use a freshly allocated internal-MIR address, function name, DefId alone,
or a truncated diagnostic. The sole public caller selects the entry body by the
same map lookup as the regular-call resolver. Overrides never fall back to source
when present, including discarded Unreachable bodies. S3 selection is preserved.

## Failure protocol

Each public `run_points_to_analysis` creates a fresh RefCell<ActiveCalls>. Nested
runs borrow it; enter checks ONLY the active stack. A completed callee is popped
and may be analyzed again with any initial graph. There is no summary cache.
Repeated active identity latches the first PointsToAnalysisError without pushing
an extra frame. The bounded message contains root, active suffix, repeated frame
index and closing identity; truncation affects display only (12 frames, 192 chars
per frame), never the matching key or allowed analysis depth.

Dataflow trait callbacks cannot return Result. Both effect callbacks stop on the
latched error. All successfully entered runs reach their single exit after solver
and cursor processing, pop their own frame, and return Err if any child failed.
An enter error returns before push. No normal/error return bypasses a matching pop;
panic recovery is not introduced. The Result boundary discards unfinished graphs,
even if error first arises while replaying the results cursor. A failed nested
run is never joined, and a failed entry root is never joined into the global graph.

The delayed pass collects root errors while continuing other root analyses with
fresh contexts. After normal instrumentation it inserts the existing Unsupported
check before the first instruction of each failed entry, using that body's span
and the cycle reason. It writes the updated body to the normal transformer cache;
this cache holds emitted bodies, not partial points-to summaries. Shared callees
are not blocked globally. No fatal compiler diagnostic or missing export is an
acceptable substitute. Successful roots retain the pre-existing target union.

## Limits

This is a prepared source fix, not evidence that the original crash cause is proven.
Real recursive ordinary roots receiving Unsupported remain release blockers. Bool,
reference-slot and captured-layout regressions remain open for separately issued
CC2/CC3. No mode qualification, verify-std scope narrowing, proof credit or Part1
GO follows from CC1. Full recursive/SCC support is outside this stage.
