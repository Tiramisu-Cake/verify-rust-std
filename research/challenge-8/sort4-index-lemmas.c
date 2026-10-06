// SPDX-License-Identifier: Apache-2.0 OR MIT
// Pure ghost theorem only; no claimed executable Rust-call proof.
//@ #include "sort4-index.gh"
/*@

lemma void s4_index_application(bool c1, bool c2, bool c3, bool c4, bool c5)
    requires true;
    ensures s4_final(c1,c2,c3,c4,c5) == true;
{
    s4_index_permutation(c1,c2,c3,c4,c5);
}
@*/
