// SPDX-License-Identifier: Apache-2.0 OR MIT
// Expected rejection of an occurrence-ID-as-rank transfer on equal keys.
//@ #include "sort4-swo.gh"
/*@
lemma void s4_wrong_rank_bridge()
    requires true;
    ensures true;
{
    s4_relation r = relation16(false,false,false,false,
                               false,false,false,false,
                               false,false,false,false,
                               false,false,false,false);
    assert s4_is_swo(r) == true;
    s4_swo_rank_bridge(r,0,1);
    assert s4_equiv(r,0,1) == true;
    assert s4_predecessors(r,0) == s4_predecessors(r,1);
    // Mutant transfer treats occurrence IDs as class ranks, despite equality.
    // TARGET_ASSERTION
    assert s4_less(r,0,1) == (0 < 1);
}
@*/
