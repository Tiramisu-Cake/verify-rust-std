"""Exact source-local S1 candidate arguments; no policy or status rewriting."""
def argument(root, p):
    f=p['file']; n=int(p['line']); ident=p['id']
    if f.endswith('/sorting_model.rs') and 'active_post::<' in ident:
        args={
          97: 'The order loop starts i=1 and executes only with i<L=before.len=values.len<=32. Thus i and i-1 are valid values indices, and i-1 cannot underflow. For the N00_01 root L<=1, the loop body has no source-feasible entry.',
          100: 'In the order loop i starts1 and increments only under i<L<=32, so i+1<=32. In N00_01 the loop body has no source-feasible entry.',
          106: 'Entry validates before.len=L<=CAP32. The outer count loop has i<L, so before.values[i] is within the 32-element snapshot array.',
          111: 'Entry validates L<=CAP32 and the inner loop has j<L. Thus before.values[j] is in bounds. old_count starts0, increments at most once per j iteration, and is <=j before the increment; its successor is <=L<=32.',
          112: 'Entry validates values.len=before.len=L<=32; inner j<L bounds values[j]. new_count starts0, increments at most once per j iteration, and is <=j before the increment; its successor is <=L<=32.',
          113: 'Inner j starts0 and increments only while j<L<=32, hence j+1<=32.',
          118: 'Outer i starts0 in the count loop and increments only while i<L<=CAP32; therefore i+1<=32 even if a prior mismatch makes this site unreachable.'}
        if n in args:
            fixed={'checker_order_corrupt':2,'checker_count_corrupt':32,'sort13_weak':13,'s4p_cell_count_corrupt':2}
            premise='Exact source entry rejects invalid snapshots, lengths above32, or unequal before/after lengths; counter induction is over this bounded entry.'
            if root in fixed: premise+=f' This negative fixture has L={fixed[root]}; early false return is preserved.'
            else: premise+=' This root has L in {0,1}, from the same initialized snapshot/slice geometry.'
            return args[n],[premise,'Only the exact generated arithmetic/bounds property is considered; the labelled postcondition is not waived.']
    if f.endswith('/num/uint_macros.rs'):
        if '::abs_diff.' in ident and n==3222:
            return 'The self<other arm computes other-self; unsigned ordering implies other>=self, so subtraction cannot underflow.',['Exact usize::abs_diff branch for all usize values.']
        if '::abs_diff.' in ident and n==3224:
            return 'The else arm has self>=other, including equality, so self-other cannot underflow.',['Exact usize::abs_diff else branch for all usize values.']
        if '::is_multiple_of.' in ident and n==3916:
            return 'The match handles rhs==0 in its separate arm; the remainder in the wildcard arm has rhs!=0. The only visible smallsort caller here uses literal2.',['Exact is_multiple_of match, with no assumption on self.']
    if f.endswith('/smallsort.rs'):
        if '::small_sort_network::<' in ident and n==350:
            return 'len/2 has the literal nonzero divisor2. This remains defined for every usize len; the N00_01 early return also prevents reaching it at source level.',['Exact concrete u8/KeyLess network instance; literal calls N0 or N1.']
        if '::small_sort_network::<' in ident and n==381:
            return 'len_div_2=floor(len/2)<=len for every usize len; len-len_div_2 cannot underflow. Additionally all four roots have len<=4<18, so no_merge returns before this site (and N0/N1 return at entry).',['Exact small_sort_network source lines339-381; no pointer-validity claim follows from subtraction.']
        if '::bidirectional_merge::<' in ident:
            if n==974:
                return 'len/2 divides by literal2, which is nonzero.',['Exact concrete u8/KeyLess merge instance; all four roots return from network before its merge call.']
            if n in (990,991,992):
                expression='len_div_2-1' if n==990 else 'len-1'
                return f'The only call in this frozen small_sort_network body follows the no_merge return, hence requires len>=18. It supplies the slice of that same len, so len_div_2=floor(len/2)>=9 and len>=18; {expression} cannot underflow. In these exact roots len<=4, so that call has no source-feasible path. This uses the caller branch, not the callee intrinsics::assume as an added premise.', ['Exact Original concrete network harness; no stubs, verified stubs or summaries; literal call lengths in {0,1,2,3,4}.','The displayed merge coordinates are source-reported; no independent emitted-path/MIR identity or generic merge theorem is claimed.']
    if f.endswith('/ub_checks.rs') and n==148 and ident=='ub_checks::is_valid_allocation_size.assertion.1':
        return 'size==0 takes the usize::MAX arm; division occurs only in the else arm where size!=0. Concrete element size u8 is1 as well.',['No allocation/ownership theorem is inferred from this arithmetic property.']
    if f.endswith('/ptr/const_ptr.rs') and n==1479 and '::is_aligned_to.' in ident:
        return 'Normal continuation follows the power-of-two test; zero is not a power of two, so align>=1 and align-1 cannot underflow.',['The non-power-of-two panic path remains present; pointer validity and alignment requirements remain separate.']
    if f.endswith('/fmt/mod.rs') and n==820 and '::from_str.' in ident:
        return 'The shift count is literal1, less than x86_64 usize width64. This generated shift-count property is defined for every s.len(); it is not a no-lost-bits or transmute-validity claim.',['Exact fmt::Arguments::from_str expression s.len()<<1|1 and x86_64 target.']
    return None,[]
