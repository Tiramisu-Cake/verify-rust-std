# Odd-copy current-cell association: checked ghost relocation

The b34 length-two/three run reached the odd copy but reported five dead-code
records inside the ghost `left_nonempty && left != src` branch. In the bounded
domain, `left` and `left_end` are each `src` or `src + 1`; therefore
`left < left_end` implies `left == src`. Those five records do not describe a
second executable odd-copy case.

The preparer now places both existing left-cell association branches in the
checked lemma `bidirectional_small_left_cell_association`. Its precondition
admits either `left == src` or `left == src + 1`, equates `last_src` with
`left`, and provides the current points-to chunk and owner for the selected
cell. It carries positive size/alignment and pointer/object limits needed for
the cell arithmetic. It has no `left_nonempty` premise. Its body checks both
left-cursor candidate addresses, calls the existing checked
`bidirectional_small_current_cell_alias` in either branch, and asserts the
selected current points-to chunk. The helper neither creates nor duplicates
permission, and it uses no entry snapshot.

At the actual odd-copy site, the `left_nonempty` branch first asserts the
derived fact `left == src`, then calls the helper. Its broad abstract contract
still makes both helper body branches independently checkable. The existing
`right == src + 1` and `right == src + 2` cases remain at the call site. The
source odd-copy statement, runtime guard, target normal and unwind posts,
entry domain, and all source/callback/destination resources are unchanged.

The preparer emits every prefix lemma as a named checked body. The runner's
`expected_bodies` list is derived from the function and lemma declarations, so
the new lemma is included automatically; confirm its execution, return and
leak records in the next artifact. Acceptance requires fresh same-input source
and stack-role admission, exact ghost stripping, all expected bodies and both
helper branches with no dead-code records, both actual callees, odd and even
paths, final panic/unwind behavior, unchanged full normal/unwind posts, and
the existing return, leak, source-identity and refinement gates. Any new
helper/precondition failure is inconclusive. This draft is Cloud-unverified;
no generated source or verifier run is included here.
