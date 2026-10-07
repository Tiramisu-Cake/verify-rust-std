// SPDX-License-Identifier: Apache-2.0 OR MIT
// Pure occurrence-ID schedule for the exact bidirectional source order.
/*@
fixpoint int fa_occ(int id, int q) { return id == q ? 1 : 0; }
fixpoint int fa_below(int q, int boundary) { return q < boundary ? 1 : 0; }
fixpoint int fa_balance(int q, int lo, int hi) {
    return fa_below(q, hi) - fa_below(q, lo);
}
fixpoint int fa_up_source(int m, int k, int a, bool up_left) {
    return up_left ? a : mg_right(m, k, a);
}
fixpoint int fa_down_source(int m, int e, int k, int d, bool down_right) {
    return down_right ? mg_right_rev(m, e, d) : mg_left_rev(m, k, d);
}
fixpoint int fa_odd_source(int m, int a, bool h) {
    return h ? a : 2 * m - a;
}
fixpoint int fa_potential(int m, int e, int k, int a, int d, int q) {
    return fa_balance(q, a, m - k + d) +
           fa_balance(q, mg_right(m, k, a), mg_n(m, e) - d);
}
fixpoint int fa_final_potential(int m, int e, int a, int d, bool h, int q) {
    return fa_balance(q, a + (e == 1 ? mg_bit(h) : 0), d) +
           fa_balance(q, 2 * m - a + (e == 1 ? mg_bit(!h) : 0),
                         mg_n(m, e) - d);
}
fixpoint int fa_count(list<int> xs, int q) {
    switch (xs) {
        case nil: return 0;
        case cons(id, tail): return fa_occ(id, q) + fa_count(tail, q);
    }
}
fixpoint list<int> fa_output(int m, int e, int k, int a, int d,
                              list<pair<bool, bool> > decisions, bool h) {
    switch (decisions) {
        case nil:
            return e == 1 ? cons(fa_odd_source(m, a, h), nil) : nil;
        case cons(ch, tail):
            return cons(fa_up_source(m, k, a, fst(ch)),
                        append(fa_output(m, e, k + 1,
                                         a + mg_bit(fst(ch)),
                                         d + mg_bit(snd(ch)), tail, h),
                               cons(fa_down_source(m, e, k, d, snd(ch)), nil)));
    }
}

// Chronological events: forward write, reverse write, next pair, odd write.
fixpoint list<pair<int, int> > fa_trace(int m, int e, int k, int a, int d,
                                        list<pair<bool, bool> > decisions, bool h) {
    switch (decisions) {
        case nil:
            return e == 1 ? cons(pair(m, fa_odd_source(m, a, h)), nil) : nil;
        case cons(ch, tail):
            return cons(pair(k, fa_up_source(m, k, a, fst(ch))),
                        cons(pair(mg_n(m, e) - 1 - k,
                                  fa_down_source(m, e, k, d, snd(ch))),
                             fa_trace(m, e, k + 1,
                                      a + mg_bit(fst(ch)),
                                      d + mg_bit(snd(ch)), tail, h)));
    }
}
fixpoint int fa_dest_count(list<pair<int, int> > trace, int p) {
    switch (trace) {
        case nil: return 0;
        case cons(write, tail):
            return fa_occ(fst(write), p) + fa_dest_count(tail, p);
    }
}
fixpoint int fa_trace_value(list<pair<int, int> > trace, int p) {
    switch (trace) {
        case nil: return -1;
        case cons(write, tail):
            return fst(write) == p ? snd(write) : fa_trace_value(tail, p);
    }
}

// This cut is valid for all integer q/x, including negative q and crossed
// cursor intervals; no 'remaining inputs form sets' assumption is used.
lemma void fa_threshold_step(int q, int x)
    requires true;
    ensures fa_below(q, x + 1) - fa_below(q, x) == fa_occ(x, q);
{
    if (q < x) {
        assert fa_below(q, x + 1) == 1 && fa_below(q, x) == 1;
    } else if (q == x) {
        assert fa_below(q, x + 1) == 1 && fa_below(q, x) == 0;
    } else {
        assert fa_below(q, x + 1) == 0 && fa_below(q, x) == 0;
    }
}

lemma void fa_pair_balance(int m, int e, int k, int a, int d,
                           bool up_left, bool down_right, int q)
    requires mg_inv(m, e, k, a, d) == true && k < m;
    ensures fa_potential(m, e, k, a, d, q) ==
            fa_occ(fa_up_source(m, k, a, up_left), q) +
            fa_occ(fa_down_source(m, e, k, d, down_right), q) +
            fa_potential(m, e, k + 1,
                         a + mg_bit(up_left), d + mg_bit(down_right), q);
{
    if (up_left) {
        fa_threshold_step(q, a);
    } else {
        fa_threshold_step(q, mg_right(m, k, a));
    }
    if (down_right) {
        fa_threshold_step(q, mg_right_rev(m, e, d));
    } else {
        fa_threshold_step(q, mg_left_rev(m, k, d));
    }
    assert fa_potential(m, e, k, a, d, q) ==
           fa_occ(fa_up_source(m, k, a, up_left), q) +
           fa_occ(fa_down_source(m, e, k, d, down_right), q) +
           fa_potential(m, e, k + 1,
                        a + mg_bit(up_left), d + mg_bit(down_right), q);
}

lemma void fa_count_append(list<int> xs, list<int> ys, int q)
    requires true;
    ensures fa_count(append(xs, ys), q) == fa_count(xs, q) + fa_count(ys, q);
{
    switch (xs) {
        case nil:
        case cons(id, tail): fa_count_append(tail, ys, q);
    }
}

lemma void fa_count_balance(int m, int e, int k, int a, int d,
                            list<pair<bool, bool> > decisions, bool h, int q)
    requires mg_inv(m, e, k, a, d) == true &&
             length(decisions) == m - k;
    ensures fa_count(fa_output(m, e, k, a, d, decisions, h), q) +
            fa_final_potential(m, e, mg_end_a(decisions, a),
                               mg_end_d(decisions, d), h, q) ==
            fa_potential(m, e, k, a, d, q);
{
    switch (decisions) {
        case nil:
            assert k == m;
            if (e == 1) {
                if (h) {
                    fa_threshold_step(q, a);
                } else {
                    fa_threshold_step(q, 2 * m - a);
                }
            }
            assert fa_count(fa_output(m, e, k, a, d, decisions, h), q) +
                   fa_final_potential(m, e, a, d, h, q) ==
                   fa_potential(m, e, k, a, d, q);
        case cons(ch, tail):
            assert k < m;
            mg_pair_step(m, e, k, a, d, fst(ch), snd(ch));
            fa_pair_balance(m, e, k, a, d, fst(ch), snd(ch), q);
            fa_count_balance(m, e, k + 1,
                             a + mg_bit(fst(ch)), d + mg_bit(snd(ch)),
                             tail, h, q);
            fa_count_append(fa_output(m, e, k + 1,
                                      a + mg_bit(fst(ch)),
                                      d + mg_bit(snd(ch)), tail, h),
                            cons(fa_down_source(m, e, k, d, snd(ch)), nil), q);
    }
}

lemma void fa_initial_balance(int m, int e, int q)
    requires m >= 1 && (e == 0 || e == 1);
    ensures fa_potential(m, e, 0, 0, 0, q) ==
            (0 <= q && q < mg_n(m, e) ? 1 : 0);
{
    if (q < 0) {
        assert fa_below(q, 0) == 1 && fa_below(q, m) == 1 &&
               fa_below(q, mg_n(m, e)) == 1;
    } else if (q < m) {
        assert fa_below(q, 0) == 0 && fa_below(q, m) == 1 &&
               fa_below(q, mg_n(m, e)) == 1;
    } else if (q < mg_n(m, e)) {
        assert fa_below(q, 0) == 0 && fa_below(q, m) == 0 &&
               fa_below(q, mg_n(m, e)) == 1;
    } else {
        assert fa_below(q, 0) == 0 && fa_below(q, m) == 0 &&
               fa_below(q, mg_n(m, e)) == 0;
    }
}

lemma void fa_final_guard_balance(int m, int e, int a, int d, bool h, int q)
    requires mg_inv(m, e, m, a, d) == true &&
             mg_guard_pass(m, e, a, d, h) == true;
    ensures fa_final_potential(m, e, a, d, h, q) == 0;
{
    if (e == 0) {
        assert a == d;
        assert 2 * m - a == mg_n(m, e) - d;
    } else {
        assert a + mg_bit(h) == d;
        assert 2 * m - a + mg_bit(!h) == mg_n(m, e) - d;
    }
}

lemma void fa_output_length(int m, int e, int k, int a, int d,
                            list<pair<bool, bool> > decisions, bool h)
    requires e == 0 || e == 1;
    ensures length(fa_output(m, e, k, a, d, decisions, h)) ==
            2 * length(decisions) + e;
{
    switch (decisions) {
        case nil:
        case cons(ch, tail):
            fa_output_length(m, e, k + 1,
                             a + mg_bit(fst(ch)), d + mg_bit(snd(ch)), tail, h);
            length_append(fa_output(m, e, k + 1,
                                    a + mg_bit(fst(ch)),
                                    d + mg_bit(snd(ch)), tail, h),
                          cons(fa_down_source(m, e, k, d, snd(ch)), nil));
    }
}

lemma void fa_trace_length(int m, int e, int k, int a, int d,
                           list<pair<bool, bool> > decisions, bool h)
    requires e == 0 || e == 1;
    ensures length(fa_trace(m, e, k, a, d, decisions, h)) ==
            2 * length(decisions) + e;
{
    switch (decisions) {
        case nil:
        case cons(ch, tail):
            fa_trace_length(m, e, k + 1,
                            a + mg_bit(fst(ch)), d + mg_bit(snd(ch)), tail, h);
    }
}

lemma void fa_destinations(int m, int e, int k, int a, int d,
                           list<pair<bool, bool> > decisions, bool h, int p)
    requires mg_inv(m, e, k, a, d) == true &&
             length(decisions) == m - k;
    ensures fa_dest_count(fa_trace(m, e, k, a, d, decisions, h), p) ==
            (k <= p && p < mg_n(m, e) - k ? 1 : 0);
{
    switch (decisions) {
        case nil:
            assert k == m;
            if (e == 0) {
                assert mg_n(m, e) - k == k;
            } else {
                assert mg_n(m, e) - k == k + 1;
            }
        case cons(ch, tail):
            assert k < m;
            mg_pair_step(m, e, k, a, d, fst(ch), snd(ch));
            fa_destinations(m, e, k + 1,
                            a + mg_bit(fst(ch)), d + mg_bit(snd(ch)),
                            tail, h, p);
            if (p == k) {
                assert p != mg_n(m, e) - 1 - k;
            } else if (p == mg_n(m, e) - 1 - k) {
                assert p != k;
            }
    }
}

lemma void fa_trace_output_at(int m, int e, int k, int a, int d,
                              list<pair<bool, bool> > decisions, bool h, int p)
    requires mg_inv(m, e, k, a, d) == true &&
             length(decisions) == m - k &&
             k <= p && p < mg_n(m, e) - k;
    ensures fa_dest_count(fa_trace(m, e, k, a, d, decisions, h), p) == 1 &&
            fa_trace_value(fa_trace(m, e, k, a, d, decisions, h), p) ==
                nth(p - k, fa_output(m, e, k, a, d, decisions, h));
{
    fa_destinations(m, e, k, a, d, decisions, h, p);
    switch (decisions) {
        case nil:
            assert k == m && e == 1 && p == m;
        case cons(ch, tail):
            assert k < m;
            if (p == k) {
                assert p != mg_n(m, e) - 1 - k;
            } else if (p == mg_n(m, e) - 1 - k) {
                fa_output_length(m, e, k + 1,
                                 a + mg_bit(fst(ch)), d + mg_bit(snd(ch)),
                                 tail, h);
                nth_append_r(fa_output(m, e, k + 1,
                                       a + mg_bit(fst(ch)),
                                       d + mg_bit(snd(ch)), tail, h),
                             cons(fa_down_source(m, e, k, d, snd(ch)), nil), 0);
            } else {
                mg_pair_step(m, e, k, a, d, fst(ch), snd(ch));
                fa_trace_output_at(m, e, k + 1,
                                   a + mg_bit(fst(ch)), d + mg_bit(snd(ch)),
                                   tail, h, p);
                fa_output_length(m, e, k + 1,
                                 a + mg_bit(fst(ch)), d + mg_bit(snd(ch)),
                                 tail, h);
                nth_append(fa_output(m, e, k + 1,
                                     a + mg_bit(fst(ch)),
                                     d + mg_bit(snd(ch)), tail, h),
                           cons(fa_down_source(m, e, k, d, snd(ch)), nil),
                           p - k - 1);
            }
    }
}

// Universal pure theorem: only the final scalar guard is assumed. Every
// comparator decision in `decisions` and odd choice h otherwise remains free.
lemma void fa_entry(int n, list<pair<bool, bool> > decisions,
                    bool h, int p, int q)
    requires n >= 2 && length(decisions) == n / 2 &&
             mg_guard_pass(n / 2, n % 2,
                           mg_end_a(decisions, 0),
                           mg_end_d(decisions, 0), h) == true;
    ensures mg_trace_safe(n / 2, n % 2, 0, 0, 0, decisions, h) == true &&
            length(fa_output(n / 2, n % 2, 0, 0, 0, decisions, h)) == n &&
            length(fa_trace(n / 2, n % 2, 0, 0, 0, decisions, h)) == n &&
            fa_dest_count(fa_trace(n / 2, n % 2, 0, 0, 0, decisions, h), p) ==
                (0 <= p && p < n ? 1 : 0) &&
            (0 <= p && p < n ?
             fa_trace_value(fa_trace(n / 2, n % 2, 0, 0, 0, decisions, h), p) ==
                 nth(p, fa_output(n / 2, n % 2, 0, 0, 0, decisions, h)) : true) &&
            fa_count(fa_output(n / 2, n % 2, 0, 0, 0, decisions, h), q) ==
                (0 <= q && q < n ? 1 : 0);
{
    mg_entry(n, decisions, h);
    int m = n / 2;
    int e = n % 2;
    assert n == mg_n(m, e) && m >= 1;
    div_rem_nonneg(n, 2);
    assert 0 <= e && e < 2;
    if (e < 1) {
        assert e == 0;
    } else {
        assert e == 1;
    }
    assert e == 0 || e == 1;
    assert mg_inv(m, e, 0, 0, 0) == true;
    assert mg_terminal(m, e, mg_end_a(decisions, 0),
                       mg_end_d(decisions, 0), h) == true;
    assert mg_inv(m, e, m, mg_end_a(decisions, 0),
                  mg_end_d(decisions, 0)) == true;
    fa_output_length(m, e, 0, 0, 0, decisions, h);
    fa_trace_length(m, e, 0, 0, 0, decisions, h);
    fa_destinations(m, e, 0, 0, 0, decisions, h, p);
    if (0 <= p && p < n) {
        fa_trace_output_at(m, e, 0, 0, 0, decisions, h, p);
    }
    fa_count_balance(m, e, 0, 0, 0, decisions, h, q);
    fa_initial_balance(m, e, q);
    fa_final_guard_balance(m, e, mg_end_a(decisions, 0),
                           mg_end_d(decisions, 0), h, q);
}
@*/
