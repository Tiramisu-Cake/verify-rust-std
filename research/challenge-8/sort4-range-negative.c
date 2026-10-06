// SPDX-License-Identifier: Apache-2.0 OR MIT
// Negative control: same scalar-domain premises, one deliberately wrong bound.
/*@
lemma void s4_range_wrong_final_endpoint(int s, int d, int stride)
    requires stride > 0 &*& (s + 4 * stride <= d || d + 4 * stride <= s);
    ensures true;
{
    // Mutant endpoint claims one extra slot fits the span.
    // TARGET_ASSERTION
    assert d + (3 + 2) * stride <= d + 4 * stride;
}
@*/
