# First FnMut accumulator — closed-type build candidate

Owner merge; phase MERGE-FIRST-CALLBACK-TYPE-FIX-2026-10-18.
T0 2026-10-18T14:13:12Z; main16:13:12Z; finishing-only16:43:12Z.
New960Cloudseconds, one Build, timeout<=900+60queue envelope; no retry/carryover.
Existing v3 coordinator. Old333/960,627retired and103/960,857retired accounts CLOSED.
Policy WORK-POLICY/COMPLETION-PLAN and Evidence Brief2026-10-17 retained.

## Before implementation: source rationale and scope

Base tool d928cb1d7ac60c257daa537fa65577f41135f832. Updated Brief for42b71cd8
observes OCAML_NON_GENERALIZABLE_TYPE_VARIABLES at translator.ml339 and paired
translator-build exit1. Line339 starts functor Make; it is not an identified
failing declaration. Causality/stage order unknown; proof_attempted=False is a
source claim. Candidate hypothesis, not a confirmed compiler diagnosis:
first_fnmut_calls=ref[] leaves a weak open polymorphic-variant row in exported
functor state. Explicitly close its intended existing type.

All variable uses inspected in pinned source:
- Definition1995, one write2955, one read6776. No other assignments/aliases.
- Writer is inside translate_fn_call(fn_call_data)(loc : Ast.loc), declaration2908.
  Pair first component is exactly that loc, not loc0 or a compiler span.
- unwind_kind maps Continue→`Continue, Cleanup _→`Cleanup, all others→`Other.
- One cons write preserves order. Consumer sorts by source location and accepts
  exact prefix[(first,`Continue)] or full[(first,`Continue);(late,`Cleanup)].
  Catch-all remains false, including Other. No variant payloads or other tags.

Authorized sole tool delta:
let first_fnmut_calls :
    (Ast.loc * [ `Continue | `Cleanup | `Other ]) list ref = ref []

No casts, Obj.magic, ignored errors, semantic rules, AST transformation behavior,
Continue/Cleanup/Other handling, ordering or predicates change. The annotation is
a build candidate until Cloud translator-build succeeds. If insufficient, stop
with concrete evidence and ask owner; do not expand the patch.

## Source/identity and validation plan

Keep compiler nightly-2026-09-25/f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f,
dependencies, kernel/model/prelude/refiner rules frozen. Update tool commit,
combined first-callback.patch and its ordered-chain hash, translator source hash,
profile SHA and dependent source/config identities only. Preserve original profile
bytes separately; historical source-bound records remain unchanged. Profile scope
label experimental-merge-first-callback-u64-v1 stays the same; new exact JSON SHA
identifies this distinct build candidate, with previous identity recorded.
No label allowlist or campaign/contract changes are needed.

Static preflight: exact tool diff; git patch-check/apply in temporary source-only
checkout; reconstructed14-patch ordered source hashes vs profile; all18 adapter
base hashes and same-source recipe closure; candidate publication and transport
limits. No local compiler/extraction/refiner/verifier or dependency install.
One independent GPT-6 Luna High reviewer, no nested delegation, GO before Build.

## Full required campaign and outcome mapping

Unchanged FIRST-CALLBACK-SEMANTIC-CARD-20261017.md defines exact actual source,
concrete-u64/F FnMut with legal effects/panic, array3/owners/thread/type/lifetime/
CURRENT F/caller-frame provenance and full normal/unwind posts. Retain fresh B1,
helpers, ordinary normal/unwind, generated admission/default-off and receiver/end/
retirement controls. Keep source-linked prefix cut before tail.read separate from
fullbody unchanged posts. First actual FnMut/HRTB, false/true CURRENT recovery,
first original Continue panic recovery, official first-unwind comparison/mutant,
resource-loss/HRTB/binder negatives and late-Cleanup refusal stay mandatory.
No matrix narrowing to compiler-only. Late Cleanup→guard Drop→Resume stays separate.

After terminal use only smallsort-brief. Build question: does a fresh receipt
confirm translator-build success and no old error? Missing=UNKNOWN; source claims
labelled. Formal question: each normal/unwind/control result separately, no proof
credit from build success. B2 remains open until full shift/gap/latepanic/cleanup/
Drop/caller posts. If Brief insufficient, save compact result and request separate
bounded admin audit; no raw evidence fallback or second Build.

## Reviewed old → new identities

| Identity | Old | New | Reason |
| --- | --- | --- | --- |
| tool | `d928cb1d7ac60c257daa537fa65577f41135f832` | `52ba7e2506af993007675269111a24d15406d58b` | sole explicit closed type annotation |
| profile_sha256 | `300fd8a7172c1644552b43c5bfda51a7c8a620f505012abd3760772df55102e3` | `84949dd9b08e6eb867b9f17b3d2149dcd41b44f219bcc369e2970bf5eca90a3f` | updated exact tool/translator/patch identities; scope label and semantic rules unchanged |
| first_callback_patch_sha256 | `b7bf867409fbf6fc6c0a9dcc25d3b286a94365380c30e4b3081dbd3f5708929d` | `df08af37966ef28a9667dd8b50e45afa2e14ecf9d716e78765e2233820a64bd3` | same baseline patch plus annotation |
| translator_source_sha256 | `fb9c7be7997fbe83016dc4258bb81f6d37af780bd7b3e21eaf6f668c8efab6b9` | `be517cc54213ee350a0dfd6e892d2affb4bfa7d2c2a42e40232a4872bd83cc9f` | two-line annotation replaces inferred ref[] |

Independent GPT-6 Luna High review GO;6synthetic session tests PASS. Static preflight14patches/16reconstructed files/14profile source hashes/18base pins PASS. Neither compilation nor proof is confirmed.
Tool worktree has only upstream remote; no own fork found. Tool commit is local; exact reconstructed tool delta and identities are published through the assigned project branch. No upstream publication.
