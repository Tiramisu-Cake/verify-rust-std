// SPDX-License-Identifier: Apache-2.0 OR MIT
// Fragment only: assemble with region-arithmetic-lemmas.c for this control.
/*@
lemma void w8_negative_len33_fits_scratch32()
    requires true;
    ensures true;
{
    w8_prefix_in_bounds(32);
    w8_split_and_prefix_facts(32);
    // TARGET_ASSERTION: this is a deliberately false fit claim.
    assert 33 <= 32;
}
@*/
