// SPDX-License-Identifier: Apache-2.0 OR MIT
// Constructive fixed finite SWO composition. Include rechecked swo-rank.c and
// its compare-exchange prerequisites before this unit; no rank bridge assumed.
/*@
fixpoint bool ms_half_pair(fixpoint(int,int,bool) rel,int m,int x,int y) {
    return !(x<y && ((x<m && y<m)||(m<=x && m<=y))) || !rel(y,x);
}
fixpoint bool ms_half_row(fixpoint(int,int,bool) rel,list<int> ids,int m,int x) {
    return forall(ids,(ms_half_pair)(rel,m,x));
}
fixpoint bool ms_halves_sorted(fixpoint(int,int,bool) rel,list<int> ids,int m) {
    return forall(ids,(ms_half_row)(rel,ids,m));
}
fixpoint bool ms_faithful(fixpoint(int,int,bool) rel,int m,int e,int k,int a,int d,
                         list<pair<bool,bool> > ds) {
    switch(ds) {
        case nil:return true;
        case cons(ch,t):return fst(ch)== !rel(m+k-a,a) &&
            snd(ch)== !rel(2*m+e-1-d,m-1-k+d) &&
            ms_faithful(rel,m,e,k+1,a+mg_bit(fst(ch)),d+mg_bit(snd(ch)),t);
    }
}
fixpoint bool ms_ordered_pair(fixpoint(int,int,bool) rel,int x,int y) {
    return !rel(y,x) && (!swo_equiv(rel,x,y) || x<y);
}
fixpoint bool ms_sorted(fixpoint(int,int,bool) rel,list<int> xs) {
    switch(xs) {
        case nil:return true;
        case cons(x,t):return forall(t,(ms_ordered_pair)(rel,x)) && ms_sorted(rel,t);
    }
}
// A source comparison is rel(right,left), and each helper negates that result.
// Equivalent immutable keys therefore select the original left occurrence at
// the front and the original right occurrence at the back.
lemma void ms_forward_tie(fixpoint(int,int,bool) rel,int m,int k,int a)
    requires swo_equiv(rel,a,m+k-a)==true;
    ensures fa_up_source(m,k,a,!rel(m+k-a,a))==a;
{
    assert !rel(m+k-a,a);
}
lemma void ms_backward_tie(fixpoint(int,int,bool) rel,int m,int e,int k,int d)
    requires swo_equiv(rel,m-1-k+d,2*m+e-1-d)==true;
    ensures fa_down_source(m,e,k,d,!rel(2*m+e-1-d,m-1-k+d))==2*m+e-1-d;
{
    assert !rel(2*m+e-1-d,m-1-k+d);
}
lemma void ms_half_row_bridge(fixpoint(int,int,bool) rel,list<int> domain,int m,int x,list<int> ys)
    requires finite_swo(rel,domain)==true && mem(x,domain)==true &&
             forall(ys,(swo_member)(domain))==true && forall(ys,(ms_half_pair)(rel,m,x))==true;
    ensures forall(ys,(mb_half_pair)((swo_rank)(rel,domain),m,x))==true;
{
    switch(ys) {
        case nil:
        case cons(y,t):
            if(x<y && ((x<m && y<m)||(m<=x && m<=y))) {
                swo_rank_bridge(rel,domain,y,x);
            }
            ms_half_row_bridge(rel,domain,m,x,t);
    }
}
lemma void ms_halves_bridge_rec(fixpoint(int,int,bool) rel,list<int> domain,int m,list<int> xs)
    requires finite_swo(rel,domain)==true && ms_halves_sorted(rel,domain,m)==true &&
             forall(domain,(swo_member)(domain))==true && forall(xs,(swo_member)(domain))==true;
    ensures forall(xs,(mb_half_row)((swo_rank)(rel,domain),domain,m))==true;
{
    switch(xs) {
        case nil:
        case cons(x,t):
            mb_at(domain,(ms_half_row)(rel,domain,m),x);
            ms_half_row_bridge(rel,domain,m,x,domain);
            ms_halves_bridge_rec(rel,domain,m,t);
    }
}
lemma void ms_halves_bridge(fixpoint(int,int,bool) rel,list<int> domain,int m)
    requires finite_swo(rel,domain)==true && ms_halves_sorted(rel,domain,m)==true;
    ensures mb_halves_sorted((swo_rank)(rel,domain),domain,m)==true;
{
    swo_domain_self(domain);
    ms_halves_bridge_rec(rel,domain,m,domain);
}
lemma void ms_decisions_bridge(fixpoint(int,int,bool) rel,int m,int e,int k,int a,int d,
                               list<pair<bool,bool> > ds)
    requires mg_inv(m,e,k,a,d)==true && length(ds)==m-k &&
             finite_swo(rel,mb_ids(nat_of_int(2*m+e),0))==true &&
             ms_faithful(rel,m,e,k,a,d,ds)==true;
    ensures mb_faithful((swo_rank)(rel,mb_ids(nat_of_int(2*m+e),0)),m,e,k,a,d,ds)==true;
{
    switch(ds) {
        case nil:
        case cons(ch,t):
            list<int> domain=mb_ids(nat_of_int(2*m+e),0);
            mg_pair_step(m,e,k,a,d,fst(ch),snd(ch));
            mb_id_member(nat_of_int(2*m+e),0,a);
            mb_id_member(nat_of_int(2*m+e),0,m+k-a);
            mb_id_member(nat_of_int(2*m+e),0,m-1-k+d);
            mb_id_member(nat_of_int(2*m+e),0,2*m+e-1-d);
            swo_rank_bridge(rel,domain,m+k-a,a);
            swo_rank_bridge(rel,domain,2*m+e-1-d,m-1-k+d);
            ms_decisions_bridge(rel,m,e,k+1,a+mg_bit(fst(ch)),d+mg_bit(snd(ch)),t);
    }
}
lemma void ms_members_snoc(list<int> xs,list<int> domain,int v)
    requires forall(xs,(swo_member)(domain))==true && mem(v,domain)==true;
    ensures forall(append(xs,cons(v,nil)),(swo_member)(domain))==true;
{
    switch(xs) {case nil:case cons(x,t):ms_members_snoc(t,domain,v);}
}
lemma void ms_output_domain(int m,int e,int k,int a,int d,list<pair<bool,bool> > ds,bool h)
    requires mg_inv(m,e,k,a,d)==true && length(ds)==m-k;
    ensures forall(fa_output(m,e,k,a,d,ds,h),(swo_member)(mb_ids(nat_of_int(2*m+e),0)))==true;
{
    switch(ds) {
        case nil:
            if(e==1)mb_id_member(nat_of_int(2*m+e),0,fa_odd_source(m,a,h));
        case cons(ch,t):
            int u=fa_up_source(m,k,a,fst(ch));int v=fa_down_source(m,e,k,d,snd(ch));
            mg_pair_step(m,e,k,a,d,fst(ch),snd(ch));
            mb_id_member(nat_of_int(2*m+e),0,u);
            mb_id_member(nat_of_int(2*m+e),0,v);
            ms_output_domain(m,e,k+1,a+mg_bit(fst(ch)),d+mg_bit(snd(ch)),t,h);
            ms_members_snoc(fa_output(m,e,k+1,a+mg_bit(fst(ch)),d+mg_bit(snd(ch)),t,h),
                             mb_ids(nat_of_int(2*m+e),0),v);
    }
}
lemma void ms_output_row_bridge(fixpoint(int,int,bool) rel,list<int> domain,int x,list<int> ys)
    requires finite_swo(rel,domain)==true && mem(x,domain)==true &&
             forall(ys,(swo_member)(domain))==true &&
             forall(ys,(mb_after)((swo_rank)(rel,domain),x))==true;
    ensures forall(ys,(ms_ordered_pair)(rel,x))==true;
{
    switch(ys) {
        case nil:
        case cons(y,t):
            swo_rank_bridge(rel,domain,y,x);
            ms_output_row_bridge(rel,domain,x,t);
    }
}
lemma void ms_output_bridge(fixpoint(int,int,bool) rel,list<int> domain,list<int> xs)
    requires finite_swo(rel,domain)==true && forall(xs,(swo_member)(domain))==true &&
             mb_sorted((swo_rank)(rel,domain),xs)==true;
    ensures ms_sorted(rel,xs)==true;
{
    switch(xs) {
        case nil:
        case cons(x,t):
            ms_output_row_bridge(rel,domain,x,t);
            ms_output_bridge(rel,domain,t);
    }
}

// Complete scalar/occurrence functional result under exactly the immutable SWO,
// original two sorted halves, and normally returning faithful source decisions.
lemma void ms_entry(int n,fixpoint(int,int,bool) rel,list<pair<bool,bool> > ds,int p,int q)
    requires n>=2 && length(ds)==n/2 &&
             finite_swo(rel,mb_ids(nat_of_int(n),0))==true &&
             ms_halves_sorted(rel,mb_ids(nat_of_int(n),0),n/2)==true &&
             ms_faithful(rel,n/2,n%2,0,0,0,ds)==true;
    ensures mg_guard_pass(n/2,n%2,mg_end_a(ds,0),mg_end_d(ds,0),mg_end_a(ds,0)<mg_end_d(ds,0))==true &&
            ms_sorted(rel,fa_output(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)))==true &&
            length(fa_output(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)))==n &&
            fa_count(fa_output(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)),q)==(0<=q && q<n?1:0) &&
            length(fa_trace(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)))==n &&
            fa_dest_count(fa_trace(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)),p)==(0<=p && p<n?1:0) &&
            (0<=p && p<n ? fa_trace_value(fa_trace(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0)),p)==
               nth(p,fa_output(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0))):true) &&
            mg_trace_safe(n/2,n%2,0,0,0,ds,mg_end_a(ds,0)<mg_end_d(ds,0))==true;
{
    int m=n/2;int e=n%2;bool h=mg_end_a(ds,0)<mg_end_d(ds,0);
    list<int> domain=mb_ids(nat_of_int(n),0);
    mg_entry(n,ds,h);
    div_rem_nonneg(n,2);
    if(e<1) { assert e==0; } else { assert e==1; }
    assert e==0 || e==1;
    ms_halves_bridge(rel,domain,m);
    ms_decisions_bridge(rel,m,e,0,0,0,ds);
    mb_entry_rank(n,(swo_rank)(rel,domain),ds,p,q);
    ms_output_domain(m,e,0,0,0,ds,h);
    ms_output_bridge(rel,domain,fa_output(m,e,0,0,0,ds,h));
    fa_entry(n,ds,h,p,q);
}
lemma void ms_sorted_positions(fixpoint(int,int,bool) rel,list<int> xs,int i,int j)
    requires ms_sorted(rel,xs)==true && 0<=i && i<j && j<length(xs);
    ensures !rel(nth(j,xs),nth(i,xs)) &&
            (swo_equiv(rel,nth(i,xs),nth(j,xs)) ? nth(i,xs)<nth(j,xs):true);
{
    switch(xs) {
        case nil:
        case cons(x,t):
            if(i==0) {
                mem_nth(j-1,t);
                mb_at(t,(ms_ordered_pair)(rel,x),nth(j-1,t));
            } else ms_sorted_positions(rel,t,i-1,j-1);
    }
}
@*/
