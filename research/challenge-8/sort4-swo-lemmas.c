// SPDX-License-Identifier: Apache-2.0 OR MIT
// Application surface for the checked finite-SWO rank bridge.
//@ #include "sort4-swo.gh"
/*@
lemma void s4_swo_rank_application(s4_relation r, int x, int y)
    requires s4_is_swo(r) == true &*& s4_id4(x) == true &*&
             s4_id4(y) == true;
    ensures s4_is_swo(r) == true &*& s4_id4(x) == true &*&
            s4_id4(y) == true &*&
            (s4_less(r,x,y) == (s4_predecessors(r,x) < s4_predecessors(r,y))) &*&
            (s4_equiv(r,x,y) == (s4_predecessors(r,x) == s4_predecessors(r,y))) &*&
            0 <= s4_predecessors(r,x) &*& s4_predecessors(r,x) <= 3 &*&
            0 <= s4_predecessors(r,y) &*& s4_predecessors(r,y) <= 3;
{
    s4_swo_rank_bridge(r,x,y);
}
@*/
