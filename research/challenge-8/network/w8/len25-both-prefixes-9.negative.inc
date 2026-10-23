// SPDX-License-Identifier: Apache-2.0 OR MIT
// Fragment only: assemble with region-arithmetic-lemmas.c for this control.
/*@
lemma void w8_negative_len25_both_prefixes_are_9()
    requires true;
    ensures true;
{
    w8_split_and_prefix_facts(25);
    // TARGET_ASSERTION: right half has prefix 13, so this is false.
    assert w8_region_prefix(w8_right_len(25)) == 9;
}
@*/
