// SPDX-License-Identifier: Apache-2.0 OR MIT
//@ #include "sort4-index.gh"
/*@

lemma void s4_wrong_hi_duplicates_min()
    requires true;
    ensures true;
{
    s4_index_permutation(false,false,false,false,false);
    // Mutant: choose min in place of hi. Other three expressions unchanged.
    // TARGET_ASSERTION
    assert s4_perm(s4_min(false,false,false),
                   s4_lo(false,false,false,false,false),
                   s4_min(false,false,false),s4_max(false,false,false)) == true;
}
@*/
