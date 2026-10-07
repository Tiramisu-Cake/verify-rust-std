// SPDX-License-Identifier: Apache-2.0 OR MIT
// Pure mathematical cursor geometry for the pinned SmallSort merge bodies.
//@ #include "list.gh"
/*@
fixpoint int mg_n(int m, int e) { return 2 * m + e; }
fixpoint int mg_left(int a) { return a; }
fixpoint int mg_right(int m, int k, int a) { return m + k - a; }
fixpoint int mg_left_rev(int m, int k, int d) { return m - 1 - k + d; }
fixpoint int mg_right_rev(int m, int e, int d) { return mg_n(m, e) - 1 - d; }
fixpoint int mg_dst_rev(int m, int e, int k) { return mg_n(m, e) - 1 - k; }
fixpoint int mg_bit(bool choice) { return choice ? 1 : 0; }

fixpoint bool mg_inv(int m, int e, int k, int a, int d) {
    return m >= 1 && (e == 0 || e == 1) &&
           0 <= a && a <= k && 0 <= d && d <= k && k <= m;
}

// Events are in Rust source order: both references, selected copy-source and
// current destination are checked before right, left, destination updates.
fixpoint bool mg_up_event(int m, int e, int k, int a, bool take_left) {
    return 0 <= mg_left(a) && mg_left(a) < mg_n(m, e) &&
           0 <= mg_right(m, k, a) && mg_right(m, k, a) < mg_n(m, e) &&
           0 <= (take_left ? mg_left(a) : mg_right(m, k, a)) &&
           (take_left ? mg_left(a) : mg_right(m, k, a)) < mg_n(m, e) &&
           0 <= k && k < mg_n(m, e) &&
           mg_right(m, k, a) <= mg_right(m, k, a) + mg_bit(!take_left) &&
           mg_right(m, k, a) + mg_bit(!take_left) <= mg_n(m, e) &&
           mg_left(a) <= mg_left(a) + mg_bit(take_left) &&
           mg_left(a) + mg_bit(take_left) <= mg_n(m, e) &&
           0 <= k + 1 && k + 1 <= mg_n(m, e) &&
           mg_left(a) + mg_bit(take_left) == a + mg_bit(take_left) &&
           mg_right(m, k, a) + mg_bit(!take_left) ==
               mg_right(m, k + 1, a + mg_bit(take_left));
}

fixpoint bool mg_down_event(int m, int e, int k, int d, bool take_right) {
    return 0 <= mg_left_rev(m, k, d) && mg_left_rev(m, k, d) < mg_n(m, e) &&
           0 <= mg_right_rev(m, e, d) && mg_right_rev(m, e, d) < mg_n(m, e) &&
           0 <= (take_right ? mg_right_rev(m, e, d) : mg_left_rev(m, k, d)) &&
           (take_right ? mg_right_rev(m, e, d) : mg_left_rev(m, k, d)) < mg_n(m, e) &&
           0 <= mg_dst_rev(m, e, k) && mg_dst_rev(m, e, k) < mg_n(m, e) &&
           1 <= mg_dst_rev(m, e, k) &&
           0 <= mg_dst_rev(m, e, k) - 1 &&
           mg_dst_rev(m, e, k) - 1 < mg_n(m, e) &&
           -1 <= mg_left_rev(m, k, d) - mg_bit(!take_right) &&
           mg_left_rev(m, k, d) - mg_bit(!take_right) <= mg_left_rev(m, k, d) &&
           0 <= mg_right_rev(m, e, d) - mg_bit(take_right) &&
           mg_right_rev(m, e, d) - mg_bit(take_right) <= mg_right_rev(m, e, d) &&
           mg_left_rev(m, k, d) - mg_bit(!take_right) ==
               mg_left_rev(m, k + 1, d + mg_bit(take_right)) &&
           mg_right_rev(m, e, d) - mg_bit(take_right) ==
               mg_right_rev(m, e, d + mg_bit(take_right)) &&
           mg_dst_rev(m, e, k) - 1 == mg_dst_rev(m, e, k + 1);
}

fixpoint int mg_end_a(list<pair<bool, bool> > decisions, int a) {
    switch (decisions) {
        case nil: return a;
        case cons(ch, tail): return mg_end_a(tail, a + mg_bit(fst(ch)));
    }
}
fixpoint int mg_end_d(list<pair<bool, bool> > decisions, int d) {
    switch (decisions) {
        case nil: return d;
        case cons(ch, tail): return mg_end_d(tail, d + mg_bit(snd(ch)));
    }
}
fixpoint int mg_write_count(list<pair<bool, bool> > decisions, int e) {
    return 2 * length(decisions) + e;
}

fixpoint bool mg_guard_pass(int m, int e, int a, int d, bool h) {
    return a + (e == 1 ? mg_bit(h) : 0) == d &&
           2 * m - a + (e == 1 ? mg_bit(!h) : 0) == mg_n(m, e) - d;
}

// Terminal facts deliberately permit either residual branch. Pointer order for
// ZST is not identified with logical-index order by this model.
fixpoint bool mg_terminal(int m, int e, int a, int d, bool h) {
    return 0 <= a && a <= m && 0 <= d && d <= m &&
           -1 <= mg_left_rev(m, m, d) && mg_left_rev(m, m, d) < m &&
           0 <= mg_right_rev(m, e, d) &&
           mg_right_rev(m, e, d) < mg_n(m, e) &&
           mg_left_rev(m, m, d) + 1 == d &&
           mg_right_rev(m, e, d) + 1 == mg_n(m, e) - d &&
           0 <= d && d <= mg_n(m, e) &&
           0 <= mg_n(m, e) - d && mg_n(m, e) - d <= mg_n(m, e) &&
           m <= mg_n(m, e) - m && 2 * m + e == mg_n(m, e) &&
           (e == 0 ?
             (mg_n(m, e) - m == m &&
              mg_dst_rev(m, e, m) == m - 1 &&
              mg_guard_pass(m, e, a, d, h) == (a == d)) :
             (0 <= a && a < mg_n(m, e) &&
              0 <= 2 * m - a && 2 * m - a < mg_n(m, e) &&
              0 <= (h ? a : 2 * m - a) &&
              (h ? a : 2 * m - a) < mg_n(m, e) &&
              0 <= m && m < mg_n(m, e) &&
              0 <= a + mg_bit(h) && a + mg_bit(h) <= mg_n(m, e) &&
              0 <= 2 * m - a + mg_bit(!h) &&
              2 * m - a + mg_bit(!h) <= mg_n(m, e) &&
              mg_n(m, e) - m == m + 1 &&
              mg_dst_rev(m, e, m) == m &&
              mg_guard_pass(m, e, a, d, h) == (a + mg_bit(h) == d)));
}

// The recursive predicate explicitly binds every observed access and update
// to the next state; nil contains the complete terminal and count obligations.
fixpoint bool mg_trace_safe(int m, int e, int k, int a, int d,
                            list<pair<bool, bool> > decisions, bool h) {
    switch (decisions) {
        case nil:
            return mg_inv(m, e, k, a, d) && k == m &&
                   mg_terminal(m, e, a, d, h);
        case cons(ch, tail):
            return mg_inv(m, e, k, a, d) && k < m &&
                   mg_up_event(m, e, k, a, fst(ch)) &&
                   mg_down_event(m, e, k, d, snd(ch)) &&
                   mg_inv(m, e, k + 1,
                          a + mg_bit(fst(ch)), d + mg_bit(snd(ch))) &&
                   mg_trace_safe(m, e, k + 1,
                                 a + mg_bit(fst(ch)), d + mg_bit(snd(ch)),
                                 tail, h);
    }
}

lemma void mg_merge_up_access(int m, int e, int k, int a, int d, bool take_left)
    requires mg_inv(m, e, k, a, d) == true && k < m;
    ensures mg_up_event(m, e, k, a, take_left) == true;
{
    int n = mg_n(m, e);
    int l = a;
    int r = m + k - a;
    int dst = k;
    assert 0 <= l && l < n;
    assert 0 <= r && r < n;
    assert 0 <= dst && dst < n;
    int selected = take_left ? l : r;
    assert 0 <= selected && selected < n;
    int r1 = r + mg_bit(!take_left);
    int l1 = l + mg_bit(take_left);
    int dst1 = dst + 1;
    assert r <= r1 && r1 <= n;
    assert l <= l1 && l1 <= n;
    assert 0 <= dst1 && dst1 <= n;
    assert l1 == a + mg_bit(take_left);
    assert r1 == mg_right(m, k + 1, a + mg_bit(take_left));
}

lemma void mg_merge_down_access(int m, int e, int k, int a, int d, bool take_right)
    requires mg_inv(m, e, k, a, d) == true && k < m;
    ensures mg_down_event(m, e, k, d, take_right) == true;
{
    int n = mg_n(m, e);
    int lr = mg_left_rev(m, k, d);
    int rr = mg_right_rev(m, e, d);
    int dst = mg_dst_rev(m, e, k);
    assert 0 <= lr && lr < n;
    assert 0 <= rr && rr < n;
    assert 1 <= dst && dst < n;
    int selected = take_right ? rr : lr;
    assert 0 <= selected && selected < n;
    int rr1 = rr - mg_bit(take_right);
    int lr1 = lr - mg_bit(!take_right);
    int dst1 = dst - 1;
    assert -1 <= lr1 && lr1 <= lr;
    assert 0 <= rr1 && rr1 <= rr;
    assert 0 <= dst1 && dst1 < n;
    assert lr1 == mg_left_rev(m, k + 1, d + mg_bit(take_right));
    assert rr1 == mg_right_rev(m, e, d + mg_bit(take_right));
    assert dst1 == mg_dst_rev(m, e, k + 1);
}

lemma void mg_pair_step(int m, int e, int k, int a, int d,
                        bool take_left, bool take_right)
    requires mg_inv(m, e, k, a, d) == true && k < m;
    ensures mg_up_event(m, e, k, a, take_left) == true &&
            mg_down_event(m, e, k, d, take_right) == true &&
            mg_inv(m, e, k + 1, a + mg_bit(take_left),
                   d + mg_bit(take_right)) == true;
{
    mg_merge_up_access(m, e, k, a, d, take_left);
    mg_merge_down_access(m, e, k, a, d, take_right);
    assert mg_inv(m, e, k + 1, a + mg_bit(take_left),
                  d + mg_bit(take_right)) == true;
}

lemma void mg_terminal_geometry(int m, int e, int a, int d, bool h)
    requires mg_inv(m, e, m, a, d) == true;
    ensures mg_terminal(m, e, a, d, h) == true;
{
    int n = mg_n(m, e);
    int left_end = d;
    int right_end = n - d;
    assert -1 <= mg_left_rev(m, m, d) && mg_left_rev(m, m, d) < m;
    assert 0 <= mg_right_rev(m, e, d) && mg_right_rev(m, e, d) < n;
    assert mg_left_rev(m, m, d) + 1 == left_end;
    assert mg_right_rev(m, e, d) + 1 == right_end;
    assert 0 <= left_end && left_end <= n;
    assert 0 <= right_end && right_end <= n;
    assert m <= n - m;
    if (e == 0) {
        assert n - m == m;
        assert mg_dst_rev(m, e, m) == m - 1;
        assert mg_guard_pass(m, e, a, d, h) == (a == d);
    } else {
        int l = a;
        int r = 2 * m - a;
        int src = h ? l : r;
        assert 0 <= l && l < n;
        assert 0 <= r && r < n;
        assert 0 <= src && src < n;
        assert 0 <= m && m < n;
        assert 0 <= l + mg_bit(h) && l + mg_bit(h) <= n;
        assert 0 <= r + mg_bit(!h) && r + mg_bit(!h) <= n;
        assert n - m == m + 1;
        assert mg_dst_rev(m, e, m) == m;
        assert mg_guard_pass(m, e, a, d, h) == (a + mg_bit(h) == d);
    }
}

lemma void mg_trace_induction(int m, int e, int k, int a, int d,
                              list<pair<bool, bool> > decisions, bool h)
    requires mg_inv(m, e, k, a, d) == true &&
             length(decisions) == m - k;
    ensures mg_trace_safe(m, e, k, a, d, decisions, h) == true &&
            mg_terminal(m, e, mg_end_a(decisions, a),
                        mg_end_d(decisions, d), h) == true;
{
    switch (decisions) {
        case nil:
            assert k == m;
            mg_terminal_geometry(m, e, a, d, h);
        case cons(ch, tail):
            assert k < m;
            mg_pair_step(m, e, k, a, d, fst(ch), snd(ch));
            mg_trace_induction(m, e, k + 1,
                               a + mg_bit(fst(ch)), d + mg_bit(snd(ch)),
                               tail, h);
    }
}

lemma void mg_destination_regions(int m, int e, int front, int back)
    requires m >= 1 && (e == 0 || e == 1) &&
             0 <= front && front < m &&
             mg_n(m, e) - m <= back && back < mg_n(m, e);
    ensures front < back &&
            0 <= front && front < mg_n(m, e) &&
            0 <= back && back < mg_n(m, e);
{}

lemma void mg_scalar_guard(int m, int e, int a, int d, bool h)
    requires mg_inv(m, e, m, a, d) == true;
    ensures mg_guard_pass(m, e, a, d, h) ==
            (e == 0 ? a == d : a + mg_bit(h) == d) &&
            (e == 1 && h == (a < d) ?
             mg_guard_pass(m, e, a, d, h) == (d == a || d == a + 1) : true);
{
    mg_terminal_geometry(m, e, a, d, h);
    if (e == 1 && h == (a < d)) {
        if (a < d) {
            assert h == true;
        } else {
            assert h == false;
        }
    }
}

// n is the actual slice length. Division facts are derived, not assumed.
lemma void mg_entry(int n, list<pair<bool, bool> > decisions, bool residual_left)
    requires n >= 2 && length(decisions) == n / 2;
    ensures mg_trace_safe(n / 2, n % 2, 0, 0, 0,
                          decisions, residual_left) == true &&
            mg_terminal(n / 2, n % 2,
                        mg_end_a(decisions, 0),
                        mg_end_d(decisions, 0), residual_left) == true &&
            n == mg_n(n / 2, n % 2) && n / 2 >= 1 &&
            mg_write_count(decisions, n % 2) == n;
{
    int m = n / 2;
    int e = n % 2;
    div_rem_nonneg(n, 2);
    assert m >= 1;
    assert e == 0 || e == 1;
    assert n == 2 * m + e;
    assert mg_inv(m, e, 0, 0, 0) == true;
    mg_trace_induction(m, e, 0, 0, 0, decisions, residual_left);
    assert mg_write_count(decisions, e) == n;
}
@*/
