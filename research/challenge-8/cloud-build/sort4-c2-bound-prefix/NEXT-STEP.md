# Next bounded full-sort4 step — C3, design only

Read-only source/full-MIR/AST analysis by explorer, integrated after the fresh
C2 review PASS. No implementation, compilation, experiment or proof for C3.
The raw collector's pending labels are preserved; independent C2 projection
review is now recorded separately. New work requires an authorized session.

Smallest next boundary: extend after C2 normal join through actual C3 normal
close/strict lifetime exit/CURRENT pair recovery/four-cell join, stopping before
C4. Actual C3 is `is_less(&*c, &*a)` at SmallSort635, annotated source241,
normal full-MIR BB62. C1/C2 direct unwind must skip C3; C3 direct unwind must
recover current resources and reach the unchanged original unwind post/leak.
Keep original std generic signature/unit return; a distinct internal helper may
expose a comparison bool only with its own freshly proved contract. Keep `c3`
and `a,b,c,d` outside the strict callback scope for later source statements.

Actual source computes `a=base+(c1 as usize)`, `b=base+(!c1 as usize)`,
`c=base+(2+c2 as usize)`, `d=base+(2+!c2 as usize)` before C3/C4. These are
pointer arithmetic; the eight `select_unpredictable` calls occur later.
First gate: derive the selected `(c,a)` owners and complementary frame from all
four c1/c2 boolean cases, with source-linked bool casts, in-bounds/distinct
addresses, provenance/permissions and CURRENT values after C2. Pointer numerical
equality alone is not permission. Existing generic `recover_pair` can take these
pointers, but `join_four_owned_cells` needs all four index-ordered CURRENT owners.
A selected-pair/frame helper, if introduced, must be proved at the same source
version before use. Retain every admissible boolean execution; no branch deletion.

C3 call receiver/tuple/reference temporaries are normal-MIR `_98`–`_103`,
first StorageLive at BB62/source241. Move only these into a third sibling scope,
with exact init/address/live/dead and object producer/free correspondence.
Unlike C1/C2 explicit `'cmp`/`'cmp2`, current C3 AST uses inferred lifetime/ref
arguments: it needs its own checked named binding and a third independent
compiler-derived Output=bool registration. Fresh source/MIR/preAST certificate,
semantic rationale and independent exact-delta review precede tool changes.
Keep default-off C1/C2 and mandatory unbound refusal gates.

C4 then calls `is_less(&*d,&*b)` at636/annotated242/BB63, using resources CURRENT
after C3. Only after C4 do selects form min/max and nested unknown-left/right;
C5 calls `is_less(&*unknown_right,&*unknown_left)` at643/249/BB70. Their resource
and selected-pointer obligations are not discharged by C2 or this note. No c3/
c4/c5/select/copy execution is credited by the completed two-comparison prefix.

Inherit raw source4/F/thread/type/positive-T-size/optional-dst domain and full
normal/unwind frame/posts/return/leak. No Copy/Freeze/purity/no-panic restriction,
caller guard assumption, MU inverse or ZST/layout implementation. Native→C1
still first requires the separately reviewed compatible strict-cut profile,
new preAST and helper proof described in the composition dependency checkpoint.
