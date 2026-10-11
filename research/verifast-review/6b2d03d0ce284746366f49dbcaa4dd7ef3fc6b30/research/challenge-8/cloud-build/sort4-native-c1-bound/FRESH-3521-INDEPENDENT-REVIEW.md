# Independent raw review — native C1 bound Build 3521e3b3

Read-only review of the integrity-checked archive
`/tmp/native-c1-bound-3521e3b3-read/evidence.tar.gz` (SHA-256
`9fe9e42f34e4b5c2b1fb8a4644d3b00ab398cf871181b9efa045455ac7979249`).
The effective translator is `381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6`;
the frozen kernel is `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
The exact source, both complete typed-MIR hashes, and paired refinement pass.
The original pre-AST remains `18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5`;
the positive post-AST is `c5fa49a0c3cf7fdaa03cb6ba22f3fd0fcd539e9fab743ee3d724716e47755a5e`.

**Verdict: incomplete, no VF0 proof credit.** The positive verifier exits 1
solely with `verified/lib.rs(228,2): dead code`. The log verifies
`interior_pointer_limits`, `split_four_owned_cells`, `recover_pair`, and
`join_four_owned_cells` before the target. It admits one strict lifetime scope,
one compiler-derived `FnMut::call_mut` with `Output=bool`, eight callback locals,
and all four source cleanup blocks. There is no target VC `error:` before the
dead-code diagnostic.

The direct callback unwind closes its comparison debt, frees the callback
scope at source 212, calls `recover_pair` and `join_four_owned_cells` at source
196–197, restores the full CURRENT source array and `foreach` with its framed
tail, retains the opaque `MaybeUninit<T>` scratch array/ownership and CURRENT
`F`/thread resources, executes the source type leaks, then executes the original
`ReturnStmt(unwinding())`. The normal callback path performs the same debt,
scope exit, pair recovery and four-cell/full-array rejoin at source 211–226.
The target trace contains one direct-unwind return and two normal returns;
all three execute function-local cleanup, consume the automatic safe-reference
postcondition, and reach `Leak check.` The `normal_false` control fails at its
explicit false assertion at source 226; `unwind_false` fails at source 210.
These controls establish path reachability through the explicit cleanup, not
the final automatic post by themselves.

The new post-AST places the direct-unwind epilogue after original root 127
`Goto 62` and before the original final normal-return chain. The normal path
jumps past it, and the direct callback unwind enters it by its unique label.
Moving this epilogue did not remove the dead-code result. The remaining original
root tail is `Label 62; Goto 63; Label 3; Goto 63; Label 63;
Return(returning($_0))`. Labels are transparent to the dead-code check;
the two `Goto 63` statements and the return share the printed location 228:2
but have distinct physical locations in `vfconsole.HashedLoc`'s table. The
normal trace executes the `Goto 63` after `Label 62` and the final return;
there is no traced entry to `Label 3`, making the
second original `Goto 63` after `Label 3` the strongest unvisited candidate.
Exact physical error-node identity is not printed. Its sole source is the
`size_of::<T>() == 0` branch at source 145. The exact stock-model constraint
or branch handling that prunes this ZST path is not established by this review.

The next authorized investigation should identify the stock `size_of`/array
constraint and MIR-to-AST reachability for that ZST branch using a fresh,
separately reviewed experiment if needed. The guard, its real runtime path,
dead-code checking, original automatic posts, and resource assertions must
remain intact. This result supplies no external `as_mut_ptr` summary, caller
guard, `sort4_stable` call-edge proof, or callable native summary.

Main-agent precision note: root131 is the unvisited candidate inferred from
complete CFG and trace; exact physically tracked error-node identity is not
printed by this verifier. All three228,2 nontransparent nodes need an explicit
location-disambiguating diagnostic before any edit. The stock size_of contract
does not require nonzero; the reason for missing zero-size path is unresolved.
