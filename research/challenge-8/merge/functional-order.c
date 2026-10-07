// SPDX-License-Identifier: Apache-2.0 OR MIT
// Exact bidirectional functional proof; include after geometry.c/functional-ids.c.
//@ #include "nat.gh"
/*@
fixpoint list<int> mb_ids(nat size, int first) {
    switch(size) { case zero: return nil; case succ(t): return cons(first,mb_ids(t,first+1)); }
}
fixpoint bool mb_lt(fixpoint(int,int) key,int x,int y) {
    return key(x)<key(y) || (key(x)==key(y) && x<y);
}
fixpoint bool mb_after(fixpoint(int,int) key,int x,int y) { return mb_lt(key,x,y); }
fixpoint bool mb_before(fixpoint(int,int) key,int y,int x) { return mb_lt(key,x,y); }
fixpoint bool mb_half_pair(fixpoint(int,int) key,int m,int x,int y) {
    return !(x<y && ((x<m && y<m)||(m<=x && m<=y))) || key(x)<=key(y);
}
fixpoint bool mb_half_row(fixpoint(int,int) key,list<int> ids,int m,int x) {
    return forall(ids,(mb_half_pair)(key,m,x));
}
fixpoint bool mb_halves_sorted(fixpoint(int,int) key,list<int> ids,int m) {
    return forall(ids,(mb_half_row)(key,ids,m));
}
fixpoint bool mb_sorted(fixpoint(int,int) key,list<int> xs) {
    switch(xs) { case nil:return true; case cons(x,t):return forall(t,(mb_after)(key,x)) && mb_sorted(key,t); }
}
fixpoint bool mb_bounds(fixpoint(int,int) key,bool haslo,int lo,bool hashi,int hi,int x) {
    return (!haslo || mb_lt(key,lo,x)) && (!hashi || mb_lt(key,x,hi));
}
fixpoint bool mb_remaining(int m,int e,int k,int a,int d,int x) {
    return (a<=x && x<m-k+d) || (m+k-a<=x && x<2*m+e-d);
}
fixpoint bool mb_remaining_bound(fixpoint(int,int) key,int m,int e,int k,int a,int d,
                                bool haslo,int lo,bool hashi,int hi,int x) {
    return !mb_remaining(m,e,k,a,d,x) || mb_bounds(key,haslo,lo,hashi,hi,x);
}
fixpoint bool mb_frontiers(fixpoint(int,int) key,int m,int e,int k,int a,int d) {
    return (a>0 && m+k-a<2*m+e ? mb_lt(key,a-1,m+k-a):true) &&
           (m+k-a>m && a<m ? mb_lt(key,m+k-a-1,a):true) &&
           (m-k+d>0 && 2*m+e-d<2*m+e ? mb_lt(key,m-k+d-1,2*m+e-d):true) &&
           (2*m+e-d>m && m-k+d<m ? mb_lt(key,2*m+e-d-1,m-k+d):true);
}
fixpoint bool mb_faithful(fixpoint(int,int) key,int m,int e,int k,int a,int d,
                         list<pair<bool,bool> > ds) {
    switch(ds) {
        case nil:return true;
        case cons(ch,t):return
            fst(ch)== !(key(m+k-a)<key(a)) &&
            snd(ch)== !(key(2*m+e-1-d)<key(m-1-k+d)) &&
            mb_faithful(key,m,e,k+1,a+mg_bit(fst(ch)),d+mg_bit(snd(ch)),t);
    }
}
lemma void mb_at(list<int> xs,fixpoint(int,bool) p,int x)
    requires forall(xs,p)==true && mem(x,xs)==true;
    ensures p(x)==true;
{
    switch(xs) {case nil:case cons(h,t):if(x!=h)mb_at(t,p,x);}
}
lemma void mb_id_member(nat size,int first,int x)
    requires first<=x && x<first+int_of_nat(size);
    ensures mem(x,mb_ids(size,first))==true;
{
    switch(size) {case zero:case succ(t):if(x!=first)mb_id_member(t,first+1,x);}
}
lemma void mb_half_order(fixpoint(int,int) key,int m,int n,int x,int y)
    requires 0<=x && x<=y && y<n && ((y<m)||(m<=x)) &&
             mb_halves_sorted(key,mb_ids(nat_of_int(n),0),m)==true;
    ensures key(x)<=key(y) && (x<y ? mb_lt(key,x,y)==true:true);
{
    mb_id_member(nat_of_int(n),0,x);
    mb_id_member(nat_of_int(n),0,y);
    mb_at(mb_ids(nat_of_int(n),0),(mb_half_row)(key,mb_ids(nat_of_int(n),0),m),x);
    mb_at(mb_ids(nat_of_int(n),0),(mb_half_pair)(key,m,x),y);
}
lemma void mb_trans(fixpoint(int,int) key,int x,int y,int z)
    requires mb_lt(key,x,y)==true && mb_lt(key,y,z)==true;
    ensures mb_lt(key,x,z)==true;
{}

// The two passes advance independently. These four inequalities capture their
// separate consumed/unconsumed cuts without assuming the joint halves nonempty.
lemma void mb_frontier_step(fixpoint(int,int) key,int m,int e,int k,int a,int d,bool up,bool down)
    requires mg_inv(m,e,k,a,d)==true && k<m &&
             mb_halves_sorted(key,mb_ids(nat_of_int(2*m+e),0),m)==true &&
             mb_frontiers(key,m,e,k,a,d)==true &&
             up== !(key(m+k-a)<key(a)) && down== !(key(2*m+e-1-d)<key(m-1-k+d));
    ensures mb_frontiers(key,m,e,k+1,a+mg_bit(up),d+mg_bit(down))==true;
{
    int n=2*m+e; int r=m+k-a; int le=m-k+d; int re=n-d;
    if(up) {
        assert mb_lt(key,a,r)==true;
        if(a+1<m && r>m) {
            mb_half_order(key,m,n,a,a+1);
            mb_trans(key,r-1,a,a+1);
        }
    } else {
        assert mb_lt(key,r,a)==true;
        if(r+1<n && a>0) {
            mb_half_order(key,m,n,r,r+1);
            mb_trans(key,a-1,r,r+1);
        }
    }
    if(down) {
        assert mb_lt(key,le-1,re-1)==true;
        if(re-1>m && le<m) {
            mb_half_order(key,m,n,re-2,re-1);
            mb_trans(key,re-2,re-1,le);
        }
    } else {
        assert mb_lt(key,re-1,le-1)==true;
        if(le-1>0 && re<n) {
            mb_half_order(key,m,n,le-2,le-1);
            mb_trans(key,le-2,le-1,re);
        }
    }
}

// A crossed left cut would force a strict cycle through an unconsumed right
// interval; the symmetric argument handles a crossed right cut.
lemma void mb_no_cross(fixpoint(int,int) key,int m,int e,int k,int a,int d)
    requires mg_inv(m,e,k,a,d)==true &&
             mb_halves_sorted(key,mb_ids(nat_of_int(2*m+e),0),m)==true &&
             mb_frontiers(key,m,e,k,a,d)==true;
    ensures a<=m-k+d && m+k-a<=2*m+e-d;
{
    int n=2*m+e;int r=m+k-a;int le=m-k+d;int re=n-d;
    if(a>le) {
        mb_half_order(key,m,n,le,a-1);
        mb_half_order(key,m,n,r,re-1);
        assert mb_lt(key,a-1,r)==true;
        assert mb_lt(key,re-1,le)==true;
        assert false;
    }
    if(r>re) {
        mb_half_order(key,m,n,re,r-1);
        mb_half_order(key,m,n,a,le-1);
        assert mb_lt(key,r-1,a)==true;
        assert mb_lt(key,le-1,re)==true;
        assert false;
    }
}

// Every selected source is inside the joint remaining set, even when one
// joint half is empty. The other pass's cut excludes selecting a stale item.
lemma void mb_pair_extremes(fixpoint(int,int) key,int m,int e,int k,int a,int d,bool up,bool down)
    requires mg_inv(m,e,k,a,d)==true && k<m &&
             mb_halves_sorted(key,mb_ids(nat_of_int(2*m+e),0),m)==true &&
             mb_frontiers(key,m,e,k,a,d)==true &&
             up== !(key(m+k-a)<key(a)) && down== !(key(2*m+e-1-d)<key(m-1-k+d));
    ensures mb_remaining(m,e,k,a,d,fa_up_source(m,k,a,up))==true &&
            mb_remaining(m,e,k,a,d,fa_down_source(m,e,k,d,down))==true &&
            mb_lt(key,fa_up_source(m,k,a,up),fa_down_source(m,e,k,d,down))==true;
{
    int n=2*m+e;int r=m+k-a;int le=m-k+d;int re=n-d;
    mb_no_cross(key,m,e,k,a,d);
    if(a==le) {
        mb_half_order(key,m,n,r,re-1);
        assert mb_lt(key,re-1,a)==true;
        assert !up;
        if(a>0) {
            assert mb_lt(key,a-1,r)==true;
            assert down;
        }
    }
    if(r==re) {
        mb_half_order(key,m,n,a,le-1);
        assert mb_lt(key,le-1,r)==true;
        assert up;
        if(r>m) {
            assert mb_lt(key,r-1,a)==true;
            assert !down;
        }
    }
    assert mb_remaining(m,e,k,a,d,fa_up_source(m,k,a,up))==true;
    assert mb_remaining(m,e,k,a,d,fa_down_source(m,e,k,d,down))==true;
    if(up) {
        if(down) {
            mb_half_order(key,m,n,r,re-1);
            assert mb_lt(key,a,re-1)==true;
        } else {
            if(a==le-1) {
                mb_half_order(key,m,n,r,re-1);
                assert false;
            }
            mb_half_order(key,m,n,a,le-1);
        }
    } else {
        if(down) {
            if(r==re-1) {
                mb_half_order(key,m,n,a,le-1);
                assert false;
            }
            mb_half_order(key,m,n,r,re-1);
        } else {
            mb_half_order(key,m,n,a,le-1);
            assert mb_lt(key,r,le-1)==true;
        }
    }
}

lemma void mb_inner_point(fixpoint(int,int) key,int m,int e,int k,int a,int d,bool up,bool down,int x)
    requires mg_inv(m,e,k,a,d)==true && k<m &&
             mb_halves_sorted(key,mb_ids(nat_of_int(2*m+e),0),m)==true &&
             up== !(key(m+k-a)<key(a)) && down== !(key(2*m+e-1-d)<key(m-1-k+d)) &&
             mb_remaining(m,e,k+1,a+mg_bit(up),d+mg_bit(down),x)==true;
    ensures mb_lt(key,fa_up_source(m,k,a,up),x)==true &&
            mb_lt(key,x,fa_down_source(m,e,k,d,down))==true;
{
    int n=2*m+e;int r=m+k-a;int le=m-k+d;int re=n-d;
    if(x<m) {
        mb_half_order(key,m,n,a,x);
        mb_half_order(key,m,n,x,le-1);
        if(up) { assert a<x; } else { assert mb_lt(key,r,a)==true; }
        if(down) { assert mb_lt(key,le-1,re-1)==true; } else { assert x<le-1; }
    } else {
        mb_half_order(key,m,n,r,x);
        mb_half_order(key,m,n,x,re-1);
        if(up) { assert mb_lt(key,a,r)==true; } else { assert r<x; }
        if(down) { assert x<re-1; } else { assert mb_lt(key,re-1,le-1)==true; }
    }
}
lemma void mb_inner_all(fixpoint(int,int) key,int m,int e,int k,int a,int d,bool up,bool down,list<int> ids)
    requires mg_inv(m,e,k,a,d)==true && k<m &&
             mb_halves_sorted(key,mb_ids(nat_of_int(2*m+e),0),m)==true &&
             up== !(key(m+k-a)<key(a)) && down== !(key(2*m+e-1-d)<key(m-1-k+d));
    ensures forall(ids,(mb_remaining_bound)(key,m,e,k+1,a+mg_bit(up),d+mg_bit(down),
                      true,fa_up_source(m,k,a,up),true,fa_down_source(m,e,k,d,down)))==true;
{
    switch(ids) {
        case nil:
        case cons(x,t):
            if(mb_remaining(m,e,k+1,a+mg_bit(up),d+mg_bit(down),x))
                mb_inner_point(key,m,e,k,a,d,up,down,x);
            mb_inner_all(key,m,e,k,a,d,up,down,t);
    }
}
lemma void mb_all_unbounded(fixpoint(int,int) key,list<int> ids,int m,int e)
    requires true;
    ensures forall(ids,(mb_remaining_bound)(key,m,e,0,0,0,false,0,false,0))==true;
{
    switch(ids) {case nil:case cons(x,t):mb_all_unbounded(key,t,m,e);}
}
lemma void mb_selected_bound(fixpoint(int,int) key,int m,int e,int k,int a,int d,
                             bool haslo,int lo,bool hashi,int hi,int x)
    requires mg_inv(m,e,k,a,d)==true && mb_remaining(m,e,k,a,d,x)==true &&
             forall(mb_ids(nat_of_int(2*m+e),0),
                    (mb_remaining_bound)(key,m,e,k,a,d,haslo,lo,hashi,hi))==true;
    ensures mb_bounds(key,haslo,lo,hashi,hi,x)==true;
{
    mb_id_member(nat_of_int(2*m+e),0,x);
    mb_at(mb_ids(nat_of_int(2*m+e),0),
          (mb_remaining_bound)(key,m,e,k,a,d,haslo,lo,hashi,hi),x);
}
lemma void mb_bounds_project(fixpoint(int,int) key,list<int> xs,int lo,int hi)
    requires forall(xs,(mb_bounds)(key,true,lo,true,hi))==true;
    ensures forall(xs,(mb_after)(key,lo))==true && forall(xs,(mb_before)(key,hi))==true;
{
    switch(xs) {case nil:case cons(x,t):mb_bounds_project(key,t,lo,hi);}
}
lemma void mb_before_append(fixpoint(int,int) key,list<int> xs,int lo,int hi)
    requires forall(xs,(mb_after)(key,lo))==true && mb_lt(key,lo,hi)==true;
    ensures forall(append(xs,cons(hi,nil)),(mb_after)(key,lo))==true;
{
    switch(xs) {case nil:case cons(x,t):mb_before_append(key,t,lo,hi);}
}
lemma void mb_sorted_snoc(fixpoint(int,int) key,list<int> xs,int hi)
    requires mb_sorted(key,xs)==true && forall(xs,(mb_before)(key,hi))==true;
    ensures mb_sorted(key,append(xs,cons(hi,nil)))==true;
{
    switch(xs) {
        case nil:
        case cons(x,t):
            mb_sorted_snoc(key,t,hi);
            mb_before_append(key,t,x,hi);
    }
}
lemma void mb_bounds_widen(fixpoint(int,int) key,list<int> xs,int u,int v,bool haslo,int lo,bool hashi,int hi)
    requires forall(xs,(mb_bounds)(key,true,u,true,v))==true &&
             mb_bounds(key,haslo,lo,hashi,hi,u)==true && mb_bounds(key,haslo,lo,hashi,hi,v)==true;
    ensures forall(xs,(mb_bounds)(key,haslo,lo,hashi,hi))==true;
{
    switch(xs) {
        case nil:
        case cons(x,t):
            if(haslo)mb_trans(key,lo,u,x);
            if(hashi)mb_trans(key,x,v,hi);
            mb_bounds_widen(key,t,u,v,haslo,lo,hashi,hi);
    }
}
lemma void mb_bounds_snoc(fixpoint(int,int) key,list<int> xs,bool haslo,int lo,bool hashi,int hi,int v)
    requires forall(xs,(mb_bounds)(key,haslo,lo,hashi,hi))==true &&
             mb_bounds(key,haslo,lo,hashi,hi,v)==true;
    ensures forall(append(xs,cons(v,nil)),(mb_bounds)(key,haslo,lo,hashi,hi))==true;
{
    switch(xs) {case nil:case cons(x,t):mb_bounds_snoc(key,t,haslo,lo,hashi,hi,v);}
}

lemma void mb_induction(fixpoint(int,int) key,int m,int e,int k,int a,int d,
                        list<pair<bool,bool> > ds,bool h,bool haslo,int lo,bool hashi,int hi)
    requires mg_inv(m,e,k,a,d)==true && length(ds)==m-k &&
             mb_halves_sorted(key,mb_ids(nat_of_int(2*m+e),0),m)==true &&
             mb_frontiers(key,m,e,k,a,d)==true && mb_faithful(key,m,e,k,a,d,ds)==true &&
             h==(mg_end_a(ds,a)<mg_end_d(ds,d)) &&
             forall(mb_ids(nat_of_int(2*m+e),0),
                    (mb_remaining_bound)(key,m,e,k,a,d,haslo,lo,hashi,hi))==true;
    ensures mg_guard_pass(m,e,mg_end_a(ds,a),mg_end_d(ds,d),h)==true &&
            mb_sorted(key,fa_output(m,e,k,a,d,ds,h))==true &&
            forall(fa_output(m,e,k,a,d,ds,h),(mb_bounds)(key,haslo,lo,hashi,hi))==true;
{
    switch(ds) {
        case nil:
            mb_no_cross(key,m,e,k,a,d);
            assert k==m;
            assert a<=d && d<=a+e;
            if(e==1) {
                int x=fa_odd_source(m,a,h);
                assert mb_remaining(m,e,k,a,d,x)==true;
                mb_selected_bound(key,m,e,k,a,d,haslo,lo,hashi,hi,x);
            }
            assert mg_guard_pass(m,e,a,d,h)==true;
        case cons(ch,t):
            mb_no_cross(key,m,e,k,a,d);
            bool up=fst(ch);bool down=snd(ch);
            int u=fa_up_source(m,k,a,up);int v=fa_down_source(m,e,k,d,down);
            mb_pair_extremes(key,m,e,k,a,d,up,down);
            mb_selected_bound(key,m,e,k,a,d,haslo,lo,hashi,hi,u);
            mb_selected_bound(key,m,e,k,a,d,haslo,lo,hashi,hi,v);
            mb_frontier_step(key,m,e,k,a,d,up,down);
            mb_inner_all(key,m,e,k,a,d,up,down,mb_ids(nat_of_int(2*m+e),0));
            mg_pair_step(m,e,k,a,d,up,down);
            mb_induction(key,m,e,k+1,a+mg_bit(up),d+mg_bit(down),t,h,true,u,true,v);
            list<int> middle=fa_output(m,e,k+1,a+mg_bit(up),d+mg_bit(down),t,h);
            mb_bounds_project(key,middle,u,v);
            mb_sorted_snoc(key,middle,v);
            mb_before_append(key,middle,u,v);
            mb_bounds_widen(key,middle,u,v,haslo,lo,hashi,hi);
            mb_bounds_snoc(key,middle,haslo,lo,hashi,hi,v);
    }
}

// All lengths are symbolic; ds drives structural induction through exactly n/2
// source iterations. The odd scalar choice is derived from final logical cuts.
lemma void mb_entry_rank(int n,fixpoint(int,int) key,list<pair<bool,bool> > ds,int p,int q)
    requires n>=2 && length(ds)==n/2 &&
             mb_halves_sorted(key,mb_ids(nat_of_int(n),0),n/2)==true &&
             mb_faithful(key,n/2,n%2,0,0,0,ds)==true;
    ensures mg_guard_pass(n/2,n%2,mg_end_a(ds,0),mg_end_d(ds,0),mg_end_a(ds,0)<mg_end_d(ds,0))==true &&
            mb_sorted(key,fa_output(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)))==true &&
            length(fa_output(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)))==n &&
            fa_count(fa_output(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)),q)==(0<=q && q<n?1:0) &&
            length(fa_trace(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)))==n &&
            fa_dest_count(fa_trace(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)),p)==(0<=p && p<n?1:0) &&
            (0<=p && p<n ? fa_trace_value(fa_trace(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)),p)==
               nth(p,fa_output(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0))):true) &&
            mg_trace_safe(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0))==true;
{
    int m=n/2;int e=n%2;bool h=mg_end_a(ds,0)<mg_end_d(ds,0);
    mg_entry(n,ds,h);
    div_rem_nonneg(n,2);
    if(e<1) { assert e==0; } else { assert e==1; }
    assert e==0 || e==1;
    assert mg_inv(m,e,0,0,0)==true;
    mb_all_unbounded(key,mb_ids(nat_of_int(n),0),m,e);
    mb_induction(key,m,e,0,0,0,ds,h,false,0,false,0);
    fa_entry(n,ds,h,p,q);
}

// Extraction exposes both key ordering and original-ID stability for any two
// output positions; equal-key occurrences are never identified.
lemma void mb_sorted_positions(fixpoint(int,int) key,list<int> xs,int i,int j)
    requires mb_sorted(key,xs)==true && 0<=i && i<j && j<length(xs);
    ensures key(nth(i,xs))<=key(nth(j,xs)) &&
            (key(nth(i,xs))==key(nth(j,xs)) ? nth(i,xs)<nth(j,xs):true);
{
    switch(xs) {
        case nil:
        case cons(x,t):
            if(i==0) {
                mem_nth(j-1,t);
                mb_at(t,(mb_after)(key,x),nth(j-1,t));
            } else mb_sorted_positions(key,t,i-1,j-1);
    }
}
@*/
