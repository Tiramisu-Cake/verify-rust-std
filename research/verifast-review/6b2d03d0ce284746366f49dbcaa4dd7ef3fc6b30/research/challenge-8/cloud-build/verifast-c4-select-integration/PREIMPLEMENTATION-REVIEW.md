# Independent preimplementation review: C4 plus pointer selector

Date: 2026-10-10. Reviewed the phase card and the pinned historical manifests,
patches, C4 profile, and ManuallyDrop candidate/review. This is a static design
review; no verifier, compiler, extractor, proof, or Cloud job was run.

## Verdict

**Conditional GO for a narrow translator-only port and isolated selector unit.**
The proposed boundary preserves the current strict-lifetime implementation if
the C4 base and kernel remain pinned, old selector certificates are confined to
the separate pointer unit, and the port gets new parent/result hashes and fresh
reviewed gates. There is no basis for copying a historical kernel or claiming
that the old C4 or selector evidence transfers to a composed profile.

## Conditions before proof dispatch

1. Pin the effective C4 translator, `src/verifast.ml`, and kernel immediately
   before applying the port. Preserve the phase-card kernel SHA
   `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c` and the
   C4 strict-lifetime scope/escape/debt/token behavior. The historical
   `cleanup-projection` delta changes only the translator; do not import the
   historical kernel or VeriFast implementation.
2. Reconcile the strict-scope insertion with R3 ghost-scope handling before
   applying patches. Both touch `translate_body`'s ghost-statement processing;
   the old patch context is not a safe mechanical application to the strict-cut
   translator. Preserve the strict marker's admission, full-unwind refusal,
   CFG scope checks, capture-only refusal, and all C4 bound-prefix paths.
3. Preserve the existing ManuallyDrop identity flag exactly once. At the shared
   call-successor construction, combine the independent predicates for
   ManuallyDrop identity lowering and the exact checked false-unwind cleanup
   calls. Do not broaden either predicate or suppress other cleanup successors.
4. Keep old source/MIR/body/line and typed-CFG certificates scoped to the
   separately prepared nine-body selector unit. The C4 sort4 prefix has a
   different source capture and MIR graph; it needs its own exact pins. Do not
   attach the selector cleanup projection to the C4 body by matching names or
   transplanting the old block numbers.
5. Produce a new translator patch/profile with exact C4 parent/result hashes.
   Review the merged diff against both inputs. The original old hashes describe
   the historical experimental chain only.
6. Run the new gates on the one effective tool: selector target and its checked
   callees/nested Drop; C4 positive and all nine intended-first-VC controls;
   cleanup OFF/partial/ON controls; altered source/callee/typed edge and
   reachable-unwind admission controls; and C4 strict-lifetime marker-OFF,
   escape, debt, owner, and token regressions. Then inspect the actual first
   select after C1–C4 CURRENT recovery with complete normal and reachable
   unwind posts. A green selector component alone is not caller composition.

The semantic bound remains the phase card's one: selector result equals the
selected original `*const T`, with thread token and raw pointer-value ownership;
no pointee permission is derived. No new native-to-C1, whole-sort4, unrestricted
generic-T/ZST, sorting, or profile-acceptance claim follows from these gates.

## Addressed risks

- The C4 profile at `203b5925` proves only its bounded four-callback prefix and
  excludes the selector. Its current checkpoint is `9240f9d4`; historical C4
  proof results keep their own source/tool/profile identities.
- Historical pointer selection passed only conditionally in the experimental
  FRAME-shadow plus cleanup-projection profile. The saved result says profile
  admission is open, generic `T`/ZST is unproved, and actual sort4 was not run.
- Cleanup projection has a narrow typed contract: exact pointer-drop and
  `MaybeUninit::assume_init` calls, their `Move` operands, destinations, normal
  and cleanup edges, and same-unit checked no-unwind callees. It must continue
  refusing changed calls and any reachable-unwind case.
- The ManuallyDrop review at `a06d3a90` approves the exact candidate for user
  review only. Its implementation removes a synthetic unwind successor for
  exact `ManuallyDrop::new` identity lowering; the current selector source uses
  `MaybeUninit`, so this is a translator regression to preserve, not a premise
  of the selector theorem. The MDnew candidate is not upstream-published.

No blocking issue remains for the stated narrow port once the strict-scope
overlap is explicitly resolved in the new delta and the conditions above are
met. The later composed result still needs its own addressed review.
