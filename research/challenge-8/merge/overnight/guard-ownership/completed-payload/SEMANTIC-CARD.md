# Exact CopyOnDrop completed payload interface — DESIGN ONLY / NOT IMPLEMENTED

AFTERNOON-MERGE-GUARD-CLOUD-2026-10-09, W2→W6. Written before any semantic
implementation. No proof/tool change or acceptance is authorized by this file
alone; user already permits a justified narrow experiment, but the following
rule still needs exact scoping, review and executable gates.

## Observed obligation and blocker

Reachable construction must preserve all CURRENT owners, package generated FBC,
entail the unchanged strong actual Drop pre, call the proved same-source actual
body, preserve its full effect through canonical post, and expose that effect to
compiler glue/caller. Root-bounds d655 advances through nonnull/objectbounds/
nooverflow but stops alignment116:90–92. Root/payload intervals remain unproved.
These geometry obligations are prerequisites, not inferred from this design.

Pinned translator gen_drop_contract (4420–4592) fixes canonical normal/unwind
post to tokens + exact three field points-to/field-own + padding. Raw-pointer
field own is true (~1515), so neither src nor dst field-own carries array/T.own.
A checked call() consumes strong pre and produces strong post; verify_expr252–273
then consumes canonical post and checks ALL residual chunks for leaks. Adding
payload to own alone cannot satisfy this fixed post. Discarding it is forbidden.
MIR Drop lowering2928–2971 calls generic drop_in_place; std/lib.rsspec604–607
returns storage but no payload/copy effect. mem::forget419–422 consumes own and
returns only thread token. These are three separate interfaces.

## Proposed completed predicate and conservation argument

Provisional exact-type predicate, nonprecise because generic T.own is nonprecise:

    completed_payload<T>(t, src, dst, len) =
        type_interp::<T>() &*&
        src[..len] |-> ?current_values &*&
        dst[..len] |-> current_values &*&
        foreach(current_values, own::<T>(t));

Retain all original pure domain/geometry facts where required. This exposes
CURRENT destination equality; simply returning old guard-own hides it because
old own has dst[..len] |-> _. Full-source own supplies fraction1, so the unchanged
actual strong post must establish src fraction f=1 before closing this predicate.
Exactly one foreach pool is carried; no generic uniqueness axiom, precision
claim, T.own splitting, bytes/address ownership creation or entry-snapshot swap.
Canonical fields bind src/dst/len; completed predicate uses those same values.
Physical fields/padding and payload remain distinct chunks.

Potential narrow translator extension: exact source-linked CopyOnDrop ADT only,
append completed_payload to canonical NORMAL post while retaining existing
canonical pre/tokens/fields/field-own/padding and compatibility/leak checks.
Method annotation must prove this from unchanged actual strong post after call().
Unwind post may not claim completed copy unless actual callee proves completion;
current direct callee on_unwind=false is itself a required conditional premise,
not permission to erase unwind checks. Other ADTs/call sites retain stock rules.
Exact source hash/ADT identity/field types and order/Drop identity/profile must be
admitted before the extension; name-only matching is insufficient. Failure to
prove resource-conserving normal/unwind composition rejects the extension.

## Caller, glue and normal forget prerequisites

Caller must obtain current scratch array and owner pool through actual seed copy,
sort4/sort8/insert_tail before source279, plus writable destination and real guard
geometry/provenance. Supplied-entry fragment does not establish these facts.
Specialized compiler glue must invoke a verified SAME-SOURCE actual Drop summary,
check its safe pre, preserve the exact completed payload and physical storage
protocol, and prove full return/leak/unwind obligations. Generic drop_in_place
spec alone grants no effect. Other guard creation at source551 (len1/mutable dst)
is outside source279 theorem; bulk len>=2 restriction cannot silently cover it.

Normal source291 forget needs a checked protocol to transfer current payload out
before consuming residual guard own, or a justified exact-type forgetting summary
that returns EXISTING payload without copying it. No empty guard-own substitution
or mem::forget lemma is presently proved. Unwind restoration refers to current
scratch values after callbacks, not entry snapshots. FnMut/Freeze alone provide
neither frame nor captured-raw-alias exclusion.

## Gates and rejection stages for a future experimental profile

1. Exact-source/ADT/Drop/profile admission: reject wrong source, field/type/layout,
   unrelated Drop or helper before summary installation; fail closed.
2. Reachable exact construction + non-False FBC positive and matched body false;
   precision/header/setup failure INCONCLUSIVE. Retain all full resources/posts.
3. Canonical safe pre → unchanged strong pre geometry: all six assertions, exact
   fraction/current list. Missing alignment/intervals refuses there.
4. Actual same-source body and count-n copy prove complete normal/unwind post;
   matched first-body false reaches actual body, no header failure credit.
5. Canonical post: prove completed payload, tokens, fields and padding, NO residual
   leaks. Negative wrong dst CURRENT values, missing owner, duplicate physical cell,
   stale snapshot and omitted source resources refuse at their exact resource/post
   obligation. Generic extra T.own is not a universal duplication oracle.
6. Source-specific glue: reachable call + exact copy post, matched false after
   glue; incorrect source/callee pin rejected before summary reuse.
7. Normal transfer/forget: retain pool once; omission/duplication/stale values
   refuse at exact normal caller post. Unwind current recovery separately gated.

Stock/six and positive-stride/generic/ZST remain explicit distinct domains. New
profile/pins/regression identities required. No full-profile acceptance from any
component pass. Tests do not prove verifier soundness.

## Critical self-review

The completed predicate is a representation of resources already returned by
actual strong Drop, not a way to mint them. The proposed post extension is
plausible only when mandatory compatibility checks derive every added chunk.
Specializing glue still needs a source/semantics argument for Rust compiler Drop
and lifetime/storage effects; passing a matcher matrix would not establish it.
Alignment and numeric disjointness may require actual allocation/reference
validity evidence absent from raw field points-to. This design remains pending;
implementing a broad kernel permission/layout axiom here is not justified.
