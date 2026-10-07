// SPDX-License-Identifier: Apache-2.0 OR MIT
// Isolated relation-stability mutant: all equal keys, reversed middle IDs.
//@ #include "sort4-index.gh"
//@ #include "sort4-swo.gh"
/*@
lemma void s4_swo_wrong_equal_middle_order()
    requires true;
    ensures true;
{
    s4_relation r = relation16(false,false,false,false,
                               false,false,false,false,
                               false,false,false,false,
                               false,false,false,false);
    assert s4_is_swo(r) == true;
    s4_index_permutation(false,false,false,false,false);
    int wrong_lo = s4_right(false,false,false,false);
    int wrong_hi = s4_left(false,false,false,false);
    assert !s4_less(r,wrong_hi,wrong_lo);
    assert s4_equiv(r,wrong_lo,wrong_hi) == true;
    // TARGET_ASSERTION
    assert !s4_less(r,wrong_hi,wrong_lo) &&
           (!s4_equiv(r,wrong_lo,wrong_hi) || wrong_lo < wrong_hi);
}
@*/
