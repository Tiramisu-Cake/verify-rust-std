// SPDX-License-Identifier: Apache-2.0 OR MIT
// Pure mathematical ghost claims; no memory, source binding, or termination.
//@ #include "region-arithmetic.gh"
/*@
lemma void w8_prefix_in_bounds(int region_len)
    requires 1 <= region_len;
    ensures 1 <= w8_region_prefix(region_len) &*&
            w8_region_prefix(region_len) <= region_len;
{
    if (region_len >= 13) {
        assert w8_region_prefix(region_len) == 13;
    } else if (region_len >= 9) {
        assert w8_region_prefix(region_len) == 9;
    } else {
        assert 1 <= region_len;
        assert w8_region_prefix(region_len) == 1;
    }
}

// Bounded case split mirrors the caller's finite scratch domain. Each branch
// makes the quotient/remainder consequence explicit instead of relying on a
// general floor-division bridge.
lemma void w8_split_and_prefix_facts(int len)
    requires 18 <= len &*& len <= 32;
    ensures 9 <= w8_left_len(len) &*& w8_left_len(len) <= 16 &*&
            9 <= w8_right_len(len) &*& w8_right_len(len) <= 16 &*&
            w8_left_len(len) + w8_right_len(len) == len &*&
            (len == 25 ?
                w8_region_prefix(w8_left_len(len)) == 9 &&
                w8_region_prefix(w8_right_len(len)) == 13
             : len <= 24 ?
                w8_region_prefix(w8_left_len(len)) == 9 &&
                w8_region_prefix(w8_right_len(len)) == 9
             :
                w8_region_prefix(w8_left_len(len)) == 13 &&
                w8_region_prefix(w8_right_len(len)) == 13) == true;
{
    if (len == 18) {
        assert w8_left_len(len) == 9;
        assert w8_right_len(len) == 9;
    } else if (len == 19) {
        assert w8_left_len(len) == 9;
        assert w8_right_len(len) == 10;
    } else if (len == 20) {
        assert w8_left_len(len) == 10;
        assert w8_right_len(len) == 10;
    } else if (len == 21) {
        assert w8_left_len(len) == 10;
        assert w8_right_len(len) == 11;
    } else if (len == 22) {
        assert w8_left_len(len) == 11;
        assert w8_right_len(len) == 11;
    } else if (len == 23) {
        assert w8_left_len(len) == 11;
        assert w8_right_len(len) == 12;
    } else if (len == 24) {
        assert w8_left_len(len) == 12;
        assert w8_right_len(len) == 12;
    } else if (len == 25) {
        assert w8_left_len(len) == 12;
        assert w8_right_len(len) == 13;
    } else if (len == 26) {
        assert w8_left_len(len) == 13;
        assert w8_right_len(len) == 13;
    } else if (len == 27) {
        assert w8_left_len(len) == 13;
        assert w8_right_len(len) == 14;
    } else if (len == 28) {
        assert w8_left_len(len) == 14;
        assert w8_right_len(len) == 14;
    } else if (len == 29) {
        assert w8_left_len(len) == 14;
        assert w8_right_len(len) == 15;
    } else if (len == 30) {
        assert w8_left_len(len) == 15;
        assert w8_right_len(len) == 15;
    } else if (len == 31) {
        assert w8_left_len(len) == 15;
        assert w8_right_len(len) == 16;
    } else {
        assert len == 32;
        assert w8_left_len(len) == 16;
        assert w8_right_len(len) == 16;
    }

    assert w8_left_len(len) + w8_right_len(len) == len;
    w8_prefix_in_bounds(w8_left_len(len));
    w8_prefix_in_bounds(w8_right_len(len));
    if (len == 25) {
        assert w8_region_prefix(w8_left_len(len)) == 9;
        assert w8_region_prefix(w8_right_len(len)) == 13;
    } else if (len <= 24) {
        assert w8_region_prefix(w8_left_len(len)) == 9;
        assert w8_region_prefix(w8_right_len(len)) == 9;
    } else {
        assert w8_region_prefix(w8_left_len(len)) == 13;
        assert w8_region_prefix(w8_right_len(len)) == 13;
    }
}

lemma void w8_prefix_choice_facts()
    requires true;
    ensures w8_region_prefix(1) == 1 &*&
            w8_region_prefix(8) == 1 &*&
            w8_region_prefix(9) == 9 &*&
            w8_region_prefix(12) == 9 &*&
            w8_region_prefix(13) == 13 &*&
            w8_region_prefix(17) == 13;
{
    assert w8_region_prefix(1) == 1;
    assert w8_region_prefix(8) == 1;
    assert w8_region_prefix(9) == 9;
    assert w8_region_prefix(12) == 9;
    assert w8_region_prefix(13) == 13;
    assert w8_region_prefix(17) == 13;
}

@*/
