# One nearest actual caller obligation: current resources after c1

Checked from actual source after the conditional callee result, 2026-10-09 14:56 UTC. This is STATIC_SOURCE_LINKED_APPLICABILITY_AND_BLOCKER, not a new executable proof or a passing actual sort4 fragment.

Source library/core/src/slice/sort/shared/smallsort.rs blob40939f922bcb6fdc7ee0d30427fa861827043827, SHA25685c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1. Callee Buildf4dc1ddf-c995-4650-a4d0-896cf14ad565, infra/proofe2b249674cbe505f2d073e0df8da023a6e6406ce, translator9cf8bc328a2a12c97b9ae04b359f8a4c59f1d561ae768f1e6bde4146d247a041. Its exact runtime is linked to current std hint.rs; profile admission remains conditional/open.

## Contract fit at the first selector

Actual first select is line637 `hint::select_unpredictable(c3, c, a)` after c1–c4. Instantiate Element=T, selector value type=*const T, condition=c3, true input=c, false input=a. The checked specialized contract requires thread_token(t) with t=currentThread, and returns that token plus result=(c3?c:a) and raw_ptr_own<T>(t,result), with false unwind. It requires no rights on either pointed-to element. All eight actual selector calls have the same raw-pointer value specialization; this is no proof of unrestricted by-value select<T> or ZST callers.

Actual source produces bool conditions from FnMut and pointer inputs from offsets within v_base[0..4]. This establishes the source/type mapping; it does not by itself establish thread token recovery after the callbacks, current cell ownership or readable referents. A current four-cell invariant would supply the pointee resources independently of the selector's raw pointer ownership. Never obtain permissions from address equality. No purity, SWO, Freeze/Copy or no-panic comparator premise is added.

## Chosen nearest missing obligation

c1 at line620 is_less(&*v_base.add(1), &*v_base) precedes every selector. It must split current cells1/0, create ordered stock shared Args, frame current cells2/3, optional dst4, F owner/thread/type resources, then close borrow debts, exit the exact comparator lifetime, recover CURRENT cells1/0 and rejoin all four cells on normal AND direct unwind. Diagnostic supplied premises are initialized four source cells+T.own, writable optional destination, F.own and thread token under the existing positive-size pointer-array domain. They have not been derived for the full actual caller; generic/ZST safety remains open.

Old O24 exact-source capture (verifiedfddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9, normalMIR667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d, readonly925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5) stops at reserved __vf_sort4_first_unwind: No such function. O19/O21 isolated pair/four-cell recovery evidence does not prove this actual continuation. Its existing scope/lifetime admission remains design-only; a same-tool exact caller certificate and verified recovery placement are required. The 9-body selector unit certificate cannot be reused as a certificate for a different caller unit.

Normal c1 recovery, panic c1 recovery, c2–c5, all eight selector linkage sites, four copies and full sort4 resources remain NOT_RUN/OPEN in this phase. No unverified actual callee summary was used and no sort4 executable run was dispatched. A new actual caller frontend/lifetime composition cannot be prepared and substantively checked in the last few minutes without expanding into a large iteration; it is left explicit rather than taking supplied fragment premises as caller facts.

Recommended next assignment: exact first-callback source/typed-MIR/AST admission and ordinary current-pair/four-cell recovery on c1 normal/direct-unwind continuations, with positive and missing-resource/edge controls. The already checked pointer selector can then be linked conditionally after c1–c4 establish the thread/current-array invariant. Profile admission gates remain separate; insertion/fallback peer work is independent.
