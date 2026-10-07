// SPDX-License-Identifier: Apache-2.0 OR MIT
// Finite strict-weak-order bridge. The domain contains occurrence IDs, not keys.
// The caller supplies one immutable, pure pullback relation throughout the proof.
//@ #include "list.gh"

/*@
fixpoint bool swo_equiv(fixpoint(int, int, bool) rel, int x, int y) {
    return !rel(x, y) && !rel(y, x);
}

fixpoint bool swo_irref_at(fixpoint(int, int, bool) rel, int x) {
    return !rel(x, x);
}
fixpoint bool swo_trans_at(fixpoint(int, int, bool) rel, int x, int y, int z) {
    return !rel(x, y) || !rel(y, z) || rel(x, z);
}
fixpoint bool swo_equiv_trans_at(fixpoint(int, int, bool) rel, int x, int y, int z) {
    return !swo_equiv(rel, x, y) || !swo_equiv(rel, y, z) || swo_equiv(rel, x, z);
}
fixpoint bool swo_trans_row(fixpoint(int, int, bool) rel, list<int> d, int x, int y) {
    return forall(d, (swo_trans_at)(rel, x, y));
}
fixpoint bool swo_equiv_trans_row(fixpoint(int, int, bool) rel, list<int> d, int x, int y) {
    return forall(d, (swo_equiv_trans_at)(rel, x, y));
}
fixpoint bool swo_trans_plane(fixpoint(int, int, bool) rel, list<int> d, int x) {
    return forall(d, (swo_trans_row)(rel, d, x));
}
fixpoint bool swo_equiv_trans_plane(fixpoint(int, int, bool) rel, list<int> d, int x) {
    return forall(d, (swo_equiv_trans_row)(rel, d, x));
}
fixpoint bool finite_swo(fixpoint(int, int, bool) rel, list<int> d) {
    return forall(d, (swo_irref_at)(rel)) &&
           forall(d, (swo_trans_plane)(rel, d)) &&
           forall(d, (swo_equiv_trans_plane)(rel, d));
}
fixpoint bool swo_pred(fixpoint(int, int, bool) rel, int id, int z) {
    return rel(z, id);
}
fixpoint int swo_rank(fixpoint(int, int, bool) rel, list<int> d, int id) {
    return count(d, (swo_pred)(rel, id));
}
fixpoint bool swo_member(list<int> d, int z) { return mem(z, d); }

lemma void swo_forall_at(list<int> xs, fixpoint(int, bool) p, int x)
    requires forall(xs, p) == true &*& mem(x, xs) == true;
    ensures p(x) == true;
{
    switch (xs) {
        case nil:
        case cons(h, t):
            if (x != h) swo_forall_at(t, p, x);
    }
}

lemma void swo_laws_at(fixpoint(int, int, bool) rel, list<int> d,
                       int x, int y, int z)
    requires finite_swo(rel, d) == true &*& mem(x, d) == true &*&
             mem(y, d) == true &*& mem(z, d) == true;
    ensures !rel(x, x) &*& swo_trans_at(rel, x, y, z) == true &*&
            swo_equiv_trans_at(rel, x, y, z) == true;
{
    swo_forall_at(d, (swo_irref_at)(rel), x);
    swo_forall_at(d, (swo_trans_plane)(rel, d), x);
    swo_forall_at(d, (swo_trans_row)(rel, d, x), y);
    swo_forall_at(d, (swo_trans_at)(rel, x, y), z);
    swo_forall_at(d, (swo_equiv_trans_plane)(rel, d), x);
    swo_forall_at(d, (swo_equiv_trans_row)(rel, d, x), y);
    swo_forall_at(d, (swo_equiv_trans_at)(rel, x, y), z);
}

// A head of a suffix is a member of the original domain. This checked
// induction also supplies the recursive count proofs with their domain facts.
lemma void swo_member_lift(list<int> xs, int h, int z)
    requires mem(z, xs) == true;
    ensures mem(z, cons(h, xs)) == true;
{}

lemma void swo_domain_extend(list<int> d, list<int> xs, int h)
    requires forall(xs, (swo_member)(d)) == true;
    ensures forall(xs, (swo_member)(cons(h, d))) == true;
{
    switch (xs) {
        case nil:
        case cons(z, tail):
            swo_domain_extend(d, tail, h);
            swo_forall_at(xs, (swo_member)(d), z);
            swo_member_lift(d, h, z);
    }
}

lemma void swo_domain_self(list<int> d)
    requires true;
    ensures forall(d, (swo_member)(d)) == true;
{
    switch (d) {
        case nil:
        case cons(h, t):
            swo_domain_self(t);
            swo_domain_extend(t, t, h);
    }
}

lemma void swo_pred_equiv(fixpoint(int, int, bool) rel, list<int> d,
                          int x, int y, int z)
    requires finite_swo(rel, d) == true &*& mem(x, d) == true &*&
             mem(y, d) == true &*& mem(z, d) == true &*&
             swo_equiv(rel, x, y) == true;
    ensures rel(z, x) == rel(z, y);
{
    swo_laws_at(rel, d, y, z, x);
    swo_laws_at(rel, d, z, y, x);
    swo_laws_at(rel, d, z, x, y);
    swo_laws_at(rel, d, x, z, y);
    if (rel(z, x)) assert rel(z, y) == true;
    if (rel(z, y)) assert rel(z, x) == true;
}

lemma void swo_equal_count_rec(fixpoint(int, int, bool) rel, list<int> d,
                               list<int> xs, int x, int y)
    requires finite_swo(rel, d) == true &*& mem(x, d) == true &*&
             mem(y, d) == true &*& swo_equiv(rel, x, y) == true &*&
             forall(xs, (swo_member)(d)) == true;
    ensures swo_rank(rel, xs, x) == swo_rank(rel, xs, y);
{
    switch (xs) {
        case nil:
        case cons(z, tail):
            swo_forall_at(xs, (swo_member)(d), z);
            swo_pred_equiv(rel, d, x, y, z);
            swo_equal_count_rec(rel, d, tail, x, y);
            assert (rel(z, x) ? 1 : 0) == (rel(z, y) ? 1 : 0);
    }
}

// If x<y, pred(x) is included in pred(y), with x itself the strict witness.
// The recursion carries one scalar indicator at a time, avoiding branching on
// the whole predecessor bit vector.
lemma void swo_strict_count_rec(fixpoint(int, int, bool) rel, list<int> d,
                                list<int> xs, int x, int y)
    requires finite_swo(rel, d) == true &*& mem(x, d) == true &*&
             mem(y, d) == true &*& rel(x, y) == true &*&
             forall(xs, (swo_member)(d)) == true;
    ensures swo_rank(rel, xs, x) <= swo_rank(rel, xs, y) &*&
            (mem(x, xs) == true ? swo_rank(rel, xs, x) < swo_rank(rel, xs, y) : true);
{
    switch (xs) {
        case nil:
        case cons(z, tail):
            swo_forall_at(xs, (swo_member)(d), z);
            swo_laws_at(rel, d, z, x, y);
            swo_strict_count_rec(rel, d, tail, x, y);
            int px = rel(z, x) ? 1 : 0;
            int py = rel(z, y) ? 1 : 0;
            assert px <= py;
            if (z == x) {
                swo_laws_at(rel, d, x, x, y);
                assert px == 0 && py == 1;
            }
            if (mem(x, tail)) {
                assert swo_rank(rel, tail, x) < swo_rank(rel, tail, y);
            }
    }
}

lemma void swo_rank_bound_rec(fixpoint(int, int, bool) rel, list<int> xs, int x)
    requires !rel(x, x);
    ensures 0 <= swo_rank(rel, xs, x) &*& swo_rank(rel, xs, x) <= length(xs) &*&
            (mem(x, xs) == true ? swo_rank(rel, xs, x) < length(xs) : true);
{
    switch (xs) {
        case nil:
        case cons(z, tail):
            swo_rank_bound_rec(rel, tail, x);
            int p = rel(z, x) ? 1 : 0;
            assert 0 <= p && p <= 1;
            if (z == x) assert p == 0;
    }
}

lemma void swo_rank_bridge(fixpoint(int, int, bool) rel, list<int> d, int x, int y)
    requires finite_swo(rel, d) == true &*& mem(x, d) == true &*& mem(y, d) == true;
    ensures rel(x, y) == (swo_rank(rel, d, x) < swo_rank(rel, d, y)) &*&
            swo_equiv(rel, x, y) == (swo_rank(rel, d, x) == swo_rank(rel, d, y)) &*&
            0 <= swo_rank(rel, d, x) &*& swo_rank(rel, d, x) < length(d) &*&
            0 <= swo_rank(rel, d, y) &*& swo_rank(rel, d, y) < length(d);
{
    swo_domain_self(d);
    swo_laws_at(rel, d, x, x, x);
    swo_laws_at(rel, d, y, y, y);
    swo_rank_bound_rec(rel, d, x);
    swo_rank_bound_rec(rel, d, y);
    if (rel(x, y)) {
        swo_strict_count_rec(rel, d, d, x, y);
    } else if (rel(y, x)) {
        swo_strict_count_rec(rel, d, d, y, x);
    } else {
        assert swo_equiv(rel, x, y) == true;
        swo_equal_count_rec(rel, d, d, x, y);
    }
    assert rel(x, y) == (swo_rank(rel, d, x) < swo_rank(rel, d, y));
    assert swo_equiv(rel, x, y) == (swo_rank(rel, d, x) == swo_rank(rel, d, y));
}

// The exact source comparator is rel(right,left). Ties select the old left ID.
lemma void swo_ce(fixpoint(int, int, bool) rel, list<int> d,
                  int left, int right, int q)
    requires finite_swo(rel, d) == true &*&
             mem(left, d) == true &*& mem(right, d) == true;
    ensures mem(ce_choose(rel(right, left), right, left), d) == true &*&
            mem(ce_choose(rel(right, left), left, right), d) == true &*&
            swo_rank(rel, d, ce_choose(rel(right, left), right, left)) ==
                ce_min(swo_rank(rel, d, left), swo_rank(rel, d, right)) &*&
            swo_rank(rel, d, ce_choose(rel(right, left), left, right)) ==
                ce_max(swo_rank(rel, d, left), swo_rank(rel, d, right)) &*&
            ce_occ(ce_choose(rel(right, left), right, left), q) +
                ce_occ(ce_choose(rel(right, left), left, right), q) ==
                ce_occ(left, q) + ce_occ(right, q);
{
    swo_rank_bridge(rel, d, right, left);
    pair_count_choice(rel(right, left), left, right, q);
    if (rel(right, left)) {
        assert swo_rank(rel, d, right) < swo_rank(rel, d, left);
    } else {
        assert swo_rank(rel, d, left) <= swo_rank(rel, d, right);
    }
}
@*/
