// SPDX-License-Identifier: Apache-2.0 OR MIT
// Pure ghost theorem for the exact five-comparison sort4_stable index network.
//@ #include "sort4-index.gh"
/*@

// Each rank denotes one equivalence class of a fixed strict weak order.
// Original occurrence identity is the logical source index, even for ZSTs.
fixpoint int s4_rank(int id, int r0, int r1, int r2, int r3) {
    return id == 0 ? r0 : id == 1 ? r1 : id == 2 ? r2 : r3;
}

fixpoint bool s4_stable_step(int first, int second,
                             int r0, int r1, int r2, int r3) {
    return s4_rank(first,r0,r1,r2,r3) < s4_rank(second,r0,r1,r2,r3) ||
           (s4_rank(first,r0,r1,r2,r3) == s4_rank(second,r0,r1,r2,r3) &&
            first < second);
}

fixpoint bool s4_sorted_stable(bool c1, bool c2, bool c3, bool c4, bool c5,
                                int r0, int r1, int r2, int r3) {
    return s4_stable_step(s4_min(c1,c2,c3),s4_lo(c1,c2,c3,c4,c5),r0,r1,r2,r3) &&
           s4_stable_step(s4_lo(c1,c2,c3,c4,c5),s4_hi(c1,c2,c3,c4,c5),r0,r1,r2,r3) &&
           s4_stable_step(s4_hi(c1,c2,c3,c4,c5),s4_max(c1,c2,c4),r0,r1,r2,r3);
}

fixpoint bool s4_cmp1(int r0, int r1, int r2, int r3) { return r1 < r0; }
fixpoint bool s4_cmp2(int r0, int r1, int r2, int r3) { return r3 < r2; }
fixpoint bool s4_cmp3(int r0, int r1, int r2, int r3) {
    return s4_rank(s4_c(s4_cmp2(r0,r1,r2,r3)),r0,r1,r2,r3) <
           s4_rank(s4_a(s4_cmp1(r0,r1,r2,r3)),r0,r1,r2,r3);
}
fixpoint bool s4_cmp4(int r0, int r1, int r2, int r3) {
    return s4_rank(s4_d(s4_cmp2(r0,r1,r2,r3)),r0,r1,r2,r3) <
           s4_rank(s4_b(s4_cmp1(r0,r1,r2,r3)),r0,r1,r2,r3);
}
fixpoint bool s4_cmp5(int r0, int r1, int r2, int r3) {
    return s4_rank(s4_right(s4_cmp1(r0,r1,r2,r3),s4_cmp2(r0,r1,r2,r3),
                            s4_cmp3(r0,r1,r2,r3),s4_cmp4(r0,r1,r2,r3)),r0,r1,r2,r3) <
           s4_rank(s4_left(s4_cmp1(r0,r1,r2,r3),s4_cmp2(r0,r1,r2,r3),
                           s4_cmp3(r0,r1,r2,r3),s4_cmp4(r0,r1,r2,r3)),r0,r1,r2,r3);
}

lemma void s4_rank_order_and_stability(int r0, int r1, int r2, int r3)
    requires true;
    ensures s4_final(s4_cmp1(r0,r1,r2,r3),s4_cmp2(r0,r1,r2,r3),
                     s4_cmp3(r0,r1,r2,r3),s4_cmp4(r0,r1,r2,r3),
                     s4_cmp5(r0,r1,r2,r3)) == true &*&
            s4_sorted_stable(s4_cmp1(r0,r1,r2,r3),s4_cmp2(r0,r1,r2,r3),
                             s4_cmp3(r0,r1,r2,r3),s4_cmp4(r0,r1,r2,r3),
                             s4_cmp5(r0,r1,r2,r3),r0,r1,r2,r3) == true;
{
    bool c1 = r1 < r0;
    bool c2 = r3 < r2;
    int a = s4_a(c1);
    int b = s4_b(c1);
    int c = s4_c(c2);
    int d = s4_d(c2);
    if (c1) {} else {}
    if (c2) {} else {}
    assert s4_stable_step(a,b,r0,r1,r2,r3) == true;
    assert s4_stable_step(c,d,r0,r1,r2,r3) == true;

    bool c3 = s4_rank(c,r0,r1,r2,r3) < s4_rank(a,r0,r1,r2,r3);
    bool c4 = s4_rank(d,r0,r1,r2,r3) < s4_rank(b,r0,r1,r2,r3);
    int first = s4_min(c1,c2,c3);
    int last = s4_max(c1,c2,c4);
    int left = s4_left(c1,c2,c3,c4);
    int right = s4_right(c1,c2,c3,c4);
    if (c3) {} else {}
    if (c4) {} else {}
    assert s4_stable_step(first,left,r0,r1,r2,r3) == true;
    assert s4_stable_step(first,right,r0,r1,r2,r3) == true;
    assert s4_stable_step(left,last,r0,r1,r2,r3) == true;
    assert s4_stable_step(right,last,r0,r1,r2,r3) == true;
    // With equal middle ranks, the source order already puts left first.
    assert s4_rank(left,r0,r1,r2,r3) != s4_rank(right,r0,r1,r2,r3) || left < right;

    bool c5 = s4_rank(right,r0,r1,r2,r3) < s4_rank(left,r0,r1,r2,r3);
    int lo = s4_lo(c1,c2,c3,c4,c5);
    int hi = s4_hi(c1,c2,c3,c4,c5);
    if (c5) {} else {}
    assert s4_stable_step(first,lo,r0,r1,r2,r3) == true;
    assert s4_stable_step(lo,hi,r0,r1,r2,r3) == true;
    assert s4_stable_step(hi,last,r0,r1,r2,r3) == true;
    assert s4_sorted_stable(c1,c2,c3,c4,c5,r0,r1,r2,r3) == true;
    s4_index_permutation(c1,c2,c3,c4,c5);
}
@*/
