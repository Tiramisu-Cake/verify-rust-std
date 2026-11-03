import re, sys, difflib
N="library/core/src/slice/sort/shared/smallsort/verify/network/"
def item(path, name):
    t=open(path).read(); i=t.index("fn "+name+"()")
    s=t.rfind("\n\n",0,i)+2
    d=0; j=t.index("{",i)
    for k in range(j,len(t)):
        d+= t[k]=="{"; d-= t[k]=="}"
        if d==0: return t[s:k+1]
def norm(s, subs):
    for a,b in subs: s=s.replace(a,b)
    s=re.sub(r"\s+"," ",s); s=re.sub(r"\(\s",'(',s); s=re.sub(r",\s\)",')',s)
    return s.replace("; ",";\n").replace("{ ","{\n").replace("] ","]\n")
def show(tag,a,b):
    print("==",tag); d=list(difflib.unified_diff(a.splitlines(),b.splitlines(),"orig","new",n=0,lineterm=""))
    print("\n".join(d[2:]) if d else "(identical)")
sol=N+"posts/perm/solver.rs"
show("arbitrary vs posts::partposts_count_u64_n8 (paths super::super::super:: -> super::)",
     norm(item(N+"posts.rs","partposts_count_u64_n8"),[]),
     norm(item(sol,"perm_arbitrary_kissat_u64_n8"),[("super::super::super::","super::")]))
show("quadratic vs perm::perm_quadratic_u64_n8 (super::super::super:: -> super::super::, super::quadratic -> quadratic)",
     norm(item(N+"posts/perm.rs","perm_quadratic_u64_n8"),[]),
     norm(item(sol,"perm_quadratic_kissat_u64_n8"),[("super::super::super::","super::super::"),("super::quadratic_counts_preserved","quadratic_counts_preserved")]))
show("arbitrary control vs posts::partposts_count_negative_u64_n8",
     norm(item(N+"posts.rs","partposts_count_negative_u64_n8"),[]),
     norm(item(sol,"perm_arbitrary_kissat_negative_u64_n8"),[("super::super::super::","super::")]))
show("quadratic control vs perm::perm_quadratic_negative_u64_n8",
     norm(item(N+"posts/perm.rs","perm_quadratic_negative_u64_n8"),[]),
     norm(item(sol,"perm_quadratic_kissat_negative_u64_n8"),[("super::super::super::","super::super::"),("super::quadratic_counts_preserved","quadratic_counts_preserved")]))
