// SPDX-License-Identifier: Apache-2.0 OR MIT
// Fragment only: assemble with region-arithmetic-lemmas.c for this control.
/*@
lemma void w8_negative_region8_prefix_is_9()
    requires true;
    ensures true;
{
    w8_prefix_choice_facts();
    w8_prefix_in_bounds(8);
    // TARGET_ASSERTION: the selector chooses prefix 1 for region length 8.
    assert w8_region_prefix(8) == 9;
}
@*/
