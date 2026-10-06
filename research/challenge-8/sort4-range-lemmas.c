// SPDX-License-Identifier: Apache-2.0 OR MIT
// Pure scalar interval theorem; it says nothing about Rust pointers/resources.
//@ #include "sort4-index.gh"
/*@
lemma void s4_mul_index_bounds(int n, int stride)
    requires stride >= 0 &*& 0 <= n &*& n <= 4;
    ensures 0 <= n * stride &*& n * stride <= 4 * stride;
{
    if (n == 0) {
    } else if (n == 1) {
    } else if (n == 2) {
    } else if (n == 3) {
    } else {
        assert n == 4;
    }
}

lemma void s4_cells_within_disjoint_spans(int s, int d, int stride,
                                          int i, int j)
    requires stride >= 0 &*& 0 <= i &*& i <= 3 &*& 0 <= j &*& j <= 3 &*&
             (s + 4 * stride <= d || d + 4 * stride <= s);
    ensures s <= s + i * stride &*&
            s + i * stride + stride <= s + 4 * stride &*&
            d <= d + j * stride &*&
            d + j * stride + stride <= d + 4 * stride &*&
            (s + i * stride + stride <= d + j * stride ||
             d + j * stride + stride <= s + i * stride);
{
    s4_mul_index_bounds(i, stride);
    s4_mul_index_bounds(j, stride);
    if (i == 0) {} else if (i == 1) {} else if (i == 2) {} else { assert i == 3; }
    if (j == 0) {} else if (j == 1) {} else if (j == 2) {} else { assert j == 3; }
    if (s + 4 * stride <= d) {
    } else {
        assert d + 4 * stride <= s;
    }
}

// Compose the exact output selection expressions with scalar cell geometry.
// Each selected source cell is paired with its corresponding destination slot;
// this does not assert anything about pointer identity, provenance or resources.
lemma void s4_selected_cells_within_disjoint_spans(bool c1, bool c2, bool c3,
                                                    bool c4, bool c5,
                                                    int s, int d, int stride)
    requires stride >= 0 &*& (s + 4 * stride <= d || d + 4 * stride <= s);
    ensures s4_final(c1,c2,c3,c4,c5) == true &*&
            s <= s + s4_min(c1,c2,c3) * stride &*&
            s + s4_min(c1,c2,c3) * stride + stride <= s + 4 * stride &*&
            d <= d &*& d + stride <= d + 4 * stride &*&
            (s + s4_min(c1,c2,c3) * stride + stride <= d ||
             d + stride <= s + s4_min(c1,c2,c3) * stride) &*&
            s <= s + s4_lo(c1,c2,c3,c4,c5) * stride &*&
            s + s4_lo(c1,c2,c3,c4,c5) * stride + stride <= s + 4 * stride &*&
            d <= d + stride &*& d + 2 * stride <= d + 4 * stride &*&
            (s + s4_lo(c1,c2,c3,c4,c5) * stride + stride <= d + stride ||
             d + 2 * stride <= s + s4_lo(c1,c2,c3,c4,c5) * stride) &*&
            s <= s + s4_hi(c1,c2,c3,c4,c5) * stride &*&
            s + s4_hi(c1,c2,c3,c4,c5) * stride + stride <= s + 4 * stride &*&
            d <= d + 2 * stride &*& d + 3 * stride <= d + 4 * stride &*&
            (s + s4_hi(c1,c2,c3,c4,c5) * stride + stride <= d + 2 * stride ||
             d + 3 * stride <= s + s4_hi(c1,c2,c3,c4,c5) * stride) &*&
            s <= s + s4_max(c1,c2,c4) * stride &*&
            s + s4_max(c1,c2,c4) * stride + stride <= s + 4 * stride &*&
            d <= d + 3 * stride &*& d + 4 * stride <= d + 4 * stride &*&
            (s + s4_max(c1,c2,c4) * stride + stride <= d + 3 * stride ||
             d + 4 * stride <= s + s4_max(c1,c2,c4) * stride);
{
    s4_index_permutation(c1,c2,c3,c4,c5);
    assert 0 <= s4_min(c1,c2,c3) &*& s4_min(c1,c2,c3) <= 3;
    assert 0 <= s4_lo(c1,c2,c3,c4,c5) &*& s4_lo(c1,c2,c3,c4,c5) <= 3;
    assert 0 <= s4_hi(c1,c2,c3,c4,c5) &*& s4_hi(c1,c2,c3,c4,c5) <= 3;
    assert 0 <= s4_max(c1,c2,c4) &*& s4_max(c1,c2,c4) <= 3;
    s4_cells_within_disjoint_spans(s,d,stride,s4_min(c1,c2,c3),0);
    s4_cells_within_disjoint_spans(s,d,stride,s4_lo(c1,c2,c3,c4,c5),1);
    s4_cells_within_disjoint_spans(s,d,stride,s4_hi(c1,c2,c3,c4,c5),2);
    s4_cells_within_disjoint_spans(s,d,stride,s4_max(c1,c2,c4),3);
}
@*/
