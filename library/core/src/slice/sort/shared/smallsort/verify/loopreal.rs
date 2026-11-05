//! LOOPREAL: invariants on the real insertion loops, with matched fixed-allocation PFCs.
//! The 8/32/128 sweep diagnoses cost; it does not prove arbitrary allocation size, generic
//! callbacks, sortedness, permutation, initialization/value validity or termination.

use super::super::{insert_tail, insertion_sort_shift_left};
use crate::mem::size_of;
use crate::{intrinsics, kani, ptr};

// One function-item type for every paired PFC/consumer; both references are actually read.
fn reading_less_u64(a: &u64, b: &u64) -> bool {
    // SAFETY: the real helper must supply initialized readable references.
    unsafe {
        let _ = ptr::read_volatile(a);
        let _ = ptr::read_volatile(b);
    }
    kani::any()
}

fn exercise_insert_tail<const N: usize>() {
    let mut backing: [u64; N] = kani::any();
    let tail: usize = kani::any();
    let probe: usize = kani::any();
    kani::assume(1 <= tail && tail < N);
    kani::assume(probe < N);
    let before = backing[probe];
    let begin = backing.as_mut_ptr();
    // SAFETY: the inclusive prefix is initialized, exclusive and inside this allocation.
    unsafe { insert_tail(begin, begin.add(tail), &mut reading_less_u64) };
    kani::assert(probe <= tail || backing[probe] == before, "loopreal: insert_tail suffix frame");
    kani::cover(tail == 1, "loopreal: insert_tail shortest prefix returns");
    kani::cover(tail == N - 1, "loopreal: insert_tail longest prefix returns");
    kani::cover(probe > tail, "loopreal: insert_tail suffix frame is exercised");
}

fn exercise_outer_loop<const N: usize>() {
    let mut backing: [u64; N] = kani::any();
    let len: usize = kani::any();
    let offset: usize = kani::any();
    let probe: usize = kani::any();
    kani::assume(1 <= len && len <= N);
    kani::assume(1 <= offset && offset <= len);
    kani::assume(probe < N);
    let before = backing[probe];
    insertion_sort_shift_left(&mut backing[..len], offset, &mut reading_less_u64);
    kani::assert(probe < len || backing[probe] == before, "loopreal: outer slice frame");
    kani::cover(offset == len, "loopreal: outer empty suffix returns");
    kani::cover(offset < len, "loopreal: outer nonempty suffix returns");
    kani::cover(len == N && offset == 1, "loopreal: outer maximal suffix returns");
    kani::cover(probe >= len, "loopreal: outer slice frame is exercised");
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_u64_backing8() {
    exercise_insert_tail::<8>();
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn outer_loop_u64_backing8() {
    exercise_outer_loop::<8>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_u64_backing32() {
    exercise_insert_tail::<32>();
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn outer_loop_u64_backing32() {
    exercise_outer_loop::<32>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_u64_backing128() {
    exercise_insert_tail::<128>();
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn outer_loop_u64_backing128() {
    exercise_outer_loop::<128>();
}

// Opt-in cfg-copy of the real outer function: same signature/body/modifies, extra false
// invariant tail == initial tail. This holds at entry and is broken by any nonempty step.
// check_packet.py checks the copy against the real function after stripping attributes.
fn insertion_sort_shift_left_false<T, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    offset: usize,
    is_less: &mut F,
) {
    let len = v.len();
    if offset == 0 || offset > len {
        intrinsics::abort_immediate();
    }

    // SAFETY: see individual comments.
    unsafe {
        // We write this basic loop directly using pointers, as when we use a
        // for loop LLVM likes to unroll this loop which we do not want.
        // SAFETY: v_end is the one-past-end pointer, and we checked that
        // offset <= len, thus tail is also in-bounds.
        let v_base = v.as_mut_ptr();
        let v_end = v_base.add(len);
        let mut tail = v_base.add(offset);
        #[cfg_attr(
            kani,
            crate::kani::loop_invariant(
                (size_of::<T>() == 0
                    || (crate::ub_checks::same_allocation(v_base, tail)
                        && crate::ub_checks::same_allocation(v_base, v_end)
                        && v_base.addr() < tail.addr()
                        && tail.addr() <= v_end.addr()
                        && (tail.addr() - v_base.addr()) % size_of::<T>() == 0))
                    && tail == v_base.wrapping_add(offset)
            )
        )]
        #[cfg_attr(
            kani,
            crate::kani::loop_modifies(&tail, ptr::slice_from_raw_parts_mut(v_base, len), is_less as *mut F)
        )]
        while tail != v_end {
            // SAFETY: v_base and tail are both valid pointers to elements, and
            // v_base < tail since we checked offset != 0.
            insert_tail(v_base, tail, is_less);

            // SAFETY: we checked that tail is not yet the one-past-end pointer.
            tail = tail.add(1);
        }
    }
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn outer_loop_false_invariant_backing8() {
    let mut backing: [u64; 8] = kani::any();
    let len: usize = kani::any();
    let offset: usize = kani::any();
    kani::assume(1 <= len && len <= backing.len());
    kani::assume(1 <= offset && offset <= len);
    insertion_sort_shift_left_false(&mut backing[..len], offset, &mut reading_less_u64);
}
