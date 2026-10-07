// SPDX-License-Identifier: Apache-2.0 OR MIT
// Conditional pure composition: exact sort4 choices under any finite SWO.
//@ #include "sort4-order.gh"
//@ #include "sort4-swo.gh"
/*@
fixpoint bool s4_swo_cmp1(s4_relation r) { return s4_less(r,1,0); }
fixpoint bool s4_swo_cmp2(s4_relation r) { return s4_less(r,3,2); }
fixpoint bool s4_swo_cmp3(s4_relation r) {
    return s4_less(r,s4_c(s4_swo_cmp2(r)),s4_a(s4_swo_cmp1(r)));
}
fixpoint bool s4_swo_cmp4(s4_relation r) {
    return s4_less(r,s4_d(s4_swo_cmp2(r)),s4_b(s4_swo_cmp1(r)));
}
fixpoint bool s4_swo_cmp5(s4_relation r) {
    return s4_less(r,
        s4_right(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp3(r),s4_swo_cmp4(r)),
        s4_left(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp3(r),s4_swo_cmp4(r)));
}

fixpoint bool s4_swo_stable_step(s4_relation r, int first, int second) {
    return !s4_less(r,second,first) &&
           (!s4_equiv(r,first,second) || first < second);
}
fixpoint bool s4_swo_sorted_stable(s4_relation r) {
    return s4_swo_stable_step(r,
               s4_min(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp3(r)),
               s4_lo(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp3(r),s4_swo_cmp4(r),s4_swo_cmp5(r))) &&
           s4_swo_stable_step(r,
               s4_lo(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp3(r),s4_swo_cmp4(r),s4_swo_cmp5(r)),
               s4_hi(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp3(r),s4_swo_cmp4(r),s4_swo_cmp5(r))) &&
           s4_swo_stable_step(r,
               s4_hi(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp3(r),s4_swo_cmp4(r),s4_swo_cmp5(r)),
               s4_max(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp4(r)));
}

lemma void s4_swo_choice_network(s4_relation r)
    requires s4_is_swo(r) == true;
    ensures s4_is_swo(r) == true &*&
            s4_final(s4_swo_cmp1(r),s4_swo_cmp2(r),s4_swo_cmp3(r),
                     s4_swo_cmp4(r),s4_swo_cmp5(r)) == true &*&
            s4_swo_sorted_stable(r) == true;
{
    int r0 = s4_predecessors(r,0);
    int r1 = s4_predecessors(r,1);
    int r2 = s4_predecessors(r,2);
    int r3 = s4_predecessors(r,3);

    // The first two actual comparison operands are (1,0) and (3,2).
    s4_swo_rank_bridge(r,1,0);
    s4_swo_rank_bridge(r,3,2);
    bool c1 = s4_swo_cmp1(r);
    bool c2 = s4_swo_cmp2(r);
    assert c1 == s4_cmp1(r0,r1,r2,r3);
    assert c2 == s4_cmp2(r0,r1,r2,r3);
    int a = s4_a(c1);
    int b = s4_b(c1);
    int c = s4_c(c2);
    int d = s4_d(c2);
    if (c1) {} else {}
    if (c2) {} else {}
    assert s4_id4(a) == true && s4_id4(b) == true;
    assert s4_id4(c) == true && s4_id4(d) == true;

    // The next two actual operands are (c,a) and (d,b).
    s4_swo_rank_bridge(r,c,a);
    s4_swo_rank_bridge(r,d,b);
    bool c3 = s4_swo_cmp3(r);
    bool c4 = s4_swo_cmp4(r);
    assert c3 == s4_cmp3(r0,r1,r2,r3);
    assert c4 == s4_cmp4(r0,r1,r2,r3);
    int left = s4_left(c1,c2,c3,c4);
    int right = s4_right(c1,c2,c3,c4);
    if (c3) {} else {}
    if (c4) {} else {}
    assert s4_id4(left) == true && s4_id4(right) == true;

    // The last actual comparison uses (unknown_right,unknown_left).
    s4_swo_rank_bridge(r,right,left);
    bool c5 = s4_swo_cmp5(r);
    assert c5 == s4_cmp5(r0,r1,r2,r3);
    s4_rank_order_and_stability(r0,r1,r2,r3);
    assert s4_final(c1,c2,c3,c4,c5) == true;
    assert s4_sorted_stable(c1,c2,c3,c4,c5,r0,r1,r2,r3) == true;

    int p0 = s4_min(c1,c2,c3);
    int p1 = s4_lo(c1,c2,c3,c4,c5);
    int p2 = s4_hi(c1,c2,c3,c4,c5);
    int p3 = s4_max(c1,c2,c4);
    if (c5) {} else {}
    assert s4_id4(p0) == true && s4_id4(p1) == true;
    assert s4_id4(p2) == true && s4_id4(p3) == true;

    // Both directions make each nondecreasing relation post explicit.
    s4_swo_rank_bridge(r,p0,p1);
    s4_swo_rank_bridge(r,p1,p0);
    s4_swo_rank_bridge(r,p1,p2);
    s4_swo_rank_bridge(r,p2,p1);
    s4_swo_rank_bridge(r,p2,p3);
    s4_swo_rank_bridge(r,p3,p2);
    assert s4_swo_stable_step(r,p0,p1) == true;
    assert s4_swo_stable_step(r,p1,p2) == true;
    assert s4_swo_stable_step(r,p2,p3) == true;
    assert s4_swo_sorted_stable(r) == true;
}
@*/
