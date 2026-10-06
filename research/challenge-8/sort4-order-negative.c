// SPDX-License-Identifier: Apache-2.0 OR MIT
// Expected VeriFast failure at TARGET_ASSERTION on the stock ghost profile.
//@ #include "sort4-index.gh"
/*@

lemma void s4_wrong_equal_middle_order()
    requires true;
    ensures true;
{
    // All ranks are equal, so the real network keeps occurrence IDs 0,1,2,3.
    // Mutant: reverse only the two middle selections (2,1 instead of 1,2).
    s4_index_permutation(false,false,false,false,false);
    assert s4_final(false,false,false,false,false) == true;
    int wrong_lo = s4_right(false,false,false,false);
    int wrong_hi = s4_left(false,false,false,false);
    // TARGET_ASSERTION
    assert wrong_lo < wrong_hi;
}
@*/
