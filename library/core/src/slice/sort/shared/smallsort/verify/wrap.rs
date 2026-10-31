//! WRAP-N2: concrete checked forwarding contracts, executing real trait entries without stubs.
//! The model is the full byte; order uses its upper seven bits. An independent by-value probe
//! is shared by the scalar pre-count and post-count. No specification calls the comparator.
//! These three concrete N2 domains do not cover every specialization or the full thresholds.

use super::super::{
    StableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl, UnstableSmallSortTypeImpl,
};
use crate::cell::Cell;
use crate::mem::MaybeUninit;
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr, slice};

/// Freeze, one byte, neither Copy nor Drop: selects the default Freeze general implementation.
#[repr(transparent)]
struct NonCopyU8(u8);

// Closed to this proof module; these projections preserve each type's complete logical value.
trait Model {
    fn model(&self) -> u8;
}

impl Model for u8 {
    fn model(&self) -> u8 {
        *self
    }
}

impl Model for Cell<u8> {
    fn model(&self) -> u8 {
        self.get()
    }
}

impl Model for NonCopyU8 {
    fn model(&self) -> u8 {
        self.0
    }
}

fn cell_less(a: &Cell<u8>, b: &Cell<u8>) -> bool {
    (a.get() >> 1) < (b.get() >> 1)
}

fn byte_less(a: &u8, b: &u8) -> bool {
    (*a >> 1) < (*b >> 1)
}

fn noncopy_less(a: &NonCopyU8, b: &NonCopyU8) -> bool {
    (a.0 >> 1) < (b.0 >> 1)
}

// Same direct address comparison as the checked SPECFIX StageA profiles on the pinned model.
fn canonical<T>(cmp: fn(&T, &T) -> bool, expected: fn(&T, &T) -> bool) -> bool {
    cmp as *const () == expected as *const ()
}

// Keep the literal in a single location for the negative control's exact expect_check.
// Return false after a rejected guard, so even that path cannot forward an unlawful callback.
fn canonical_guard(ok: bool) -> bool {
    kani::assert(ok, "wrap canonical comparator required");
    ok
}

fn pair_region<T>(v: *mut T) -> bool {
    can_dereference(ptr::slice_from_raw_parts(v, 2))
        && can_write(ptr::slice_from_raw_parts_mut(v, 2))
}

// The raw interface must retain the exclusivity previously supplied by two &mut slices.
fn stable_region(v: *mut Cell<u8>, scratch: &[MaybeUninit<Cell<u8>>]) -> bool {
    pair_region(v)
        && (scratch.is_empty()
            || !same_allocation(v as *const Cell<u8>, scratch.as_ptr().cast::<Cell<u8>>())
            || {
                // SAFETY: both nonempty regions are live and in the same allocation.
                // MaybeUninit<Cell<u8>> and Cell<u8> have identical size and alignment.
                let d = unsafe { scratch.as_ptr().cast::<Cell<u8>>().offset_from(v) };
                if d >= 0 { d as usize >= 2 } else { d.unsigned_abs() >= scratch.len() }
            })
}

// Both helpers read only the two initialized input elements, never any scratch or uninit tail.
fn sorted<T: Model>(v: &[T]) -> bool {
    (v[0].model() >> 1) <= (v[1].model() >> 1)
}

fn count<T: Model>(v: &[T], probe: u8) -> usize {
    (v[0].model() == probe) as usize + (v[1].model() == probe) as usize
}

// Raw pair arguments avoid conflicting generated captures of an &mut slice on the pinned
// contract macros (G1 E0502). The raw span is always exactly N2; these adapters use the same
// pure checker as the corruption control. Only the scalar count is captured in old().
fn pair_sorted<T: Model>(v: *const T) -> bool {
    // SAFETY: the wrapper requires establish a readable initialized two-element span.
    sorted(unsafe { slice::from_raw_parts(v, 2) })
}

fn pair_count<T: Model>(v: *const T, probe: u8) -> usize {
    // SAFETY: the wrapper requires establish a readable initialized two-element span.
    count(unsafe { slice::from_raw_parts(v, 2) }, probe)
}

// Cell is !Freeze: the default Stable entry ignores scratch and runs insertion from index 1.
// Only the input slice is writable in the frame; even initialized caller scratch is untouched.
#[kani::requires(stable_region(v, scratch))]
#[kani::requires(canonical(cmp, cell_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 2))]
#[kani::ensures(|_| pair_sorted(v))]
#[kani::ensures(|_| old(pair_count(v, probe)) == pair_count(v, probe))]
unsafe fn stable_cell(
    v: *mut Cell<u8>,
    scratch: &mut [MaybeUninit<Cell<u8>>],
    cmp: fn(&Cell<u8>, &Cell<u8>) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, cell_less)) {
        return;
    }
    // SAFETY: the requires establish exactly two initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 2) };
    let mut is_less = cmp;
    <Cell<u8> as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less);
}

// u8 is Freeze + Copy and has efficient swap: network route, insertion only at N2.
#[kani::requires(pair_region(v))]
#[kani::requires(canonical(cmp, byte_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 2))]
#[kani::ensures(|_| pair_sorted(v))]
#[kani::ensures(|_| old(pair_count(v, probe)) == pair_count(v, probe))]
unsafe fn unstable_byte(v: *mut u8, cmp: fn(&u8, &u8) -> bool, probe: u8) {
    if !canonical_guard(canonical(cmp, byte_less)) {
        return;
    }
    // SAFETY: the requires establish exactly two initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 2) };
    let mut is_less = cmp;
    <u8 as UnstableSmallSortTypeImpl>::small_sort(v, &mut is_less);
}

// NonCopyU8 is Freeze but !Copy; 1 * 48 <= 4096 selects general, with private local scratch.
// At N2 general copies two singleton halves, merges into v and forgets the panic copy-back guard.
#[kani::requires(pair_region(v))]
#[kani::requires(canonical(cmp, noncopy_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 2))]
#[kani::ensures(|_| pair_sorted(v))]
#[kani::ensures(|_| old(pair_count(v, probe)) == pair_count(v, probe))]
unsafe fn freeze_noncopy(v: *mut NonCopyU8, cmp: fn(&NonCopyU8, &NonCopyU8) -> bool, probe: u8) {
    if !canonical_guard(canonical(cmp, noncopy_less)) {
        return;
    }
    // SAFETY: the requires establish exactly two initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 2) };
    let mut is_less = cmp;
    <NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut is_less);
}

fn input_covers(a: u8, b: u8, probe: u8) {
    kani::cover((a >> 1) > (b >> 1), "wrap reversed keys return");
    kani::cover((a >> 1) < (b >> 1), "wrap increasing keys return");
    kani::cover(a != b && (a >> 1) == (b >> 1), "wrap tied keys retain distinct full values");
    kani::cover(a == b, "wrap duplicate full values return");
    kani::cover(probe == a || probe == b, "wrap independent probe hits input");
    kani::cover(probe != a && probe != b, "wrap independent probe misses input");
}

#[kani::proof_for_contract(stable_cell)]
#[kani::unwind(16)]
fn stable_cell_n2() {
    let [left, a, b, right]: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [Cell::new(left), Cell::new(a), Cell::new(b), Cell::new(right)];
    let mut scratch = [MaybeUninit::new(Cell::new(kani::any())), MaybeUninit::uninit()];
    let scratch_len: usize = kani::any_where(|n: &usize| *n <= 2);
    // SAFETY: this slot was initialized above; Cell has no padding and get reads its full value.
    let scratch_before = unsafe { scratch[0].assume_init_ref() }.get();
    // SAFETY: active pair in initialized backing4; separate valid scratch; canonical pointer.
    unsafe { stable_cell(v[1..3].as_mut_ptr(), &mut scratch[..scratch_len], cell_less, probe) };
    kani::assert(v[0].get() == left && v[3].get() == right, "wrap stable input frame");
    // SAFETY: the default Cell route does not write scratch; only the input may be modified.
    let scratch_after = unsafe { scratch[0].assume_init_ref() }.get();
    kani::assert(scratch_before == scratch_after, "wrap stable scratch frame");
    kani::cover(scratch_len == 0, "wrap stable empty scratch returns");
    kani::cover(scratch_len == 2, "wrap stable unread uninit scratch tail returns");
    input_covers(a, b, probe);
    kani::cover(true, "wrap stable Cell trait entry returns");
}

#[kani::proof_for_contract(unstable_byte)]
#[kani::unwind(16)]
fn unstable_byte_n2() {
    let [left, a, b, right]: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [left, a, b, right];
    // SAFETY: active pair in initialized backing4; canonical pointer.
    unsafe { unstable_byte(v[1..3].as_mut_ptr(), byte_less, probe) };
    kani::assert(v[0] == left && v[3] == right, "wrap unstable input frame");
    input_covers(a, b, probe);
    kani::cover(true, "wrap unstable u8 trait entry returns");
}

#[kani::proof_for_contract(freeze_noncopy)]
#[kani::unwind(16)]
fn freeze_noncopy_n2() {
    let [left, a, b, right]: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [NonCopyU8(left), NonCopyU8(a), NonCopyU8(b), NonCopyU8(right)];
    // SAFETY: active pair in initialized backing4; canonical pointer.
    unsafe { freeze_noncopy(v[1..3].as_mut_ptr(), noncopy_less, probe) };
    kani::assert(v[0].0 == left && v[3].0 == right, "wrap Freeze input frame");
    input_covers(a, b, probe);
    kani::cover(true, "wrap Freeze NonCopyU8 trait entry returns");
}

fn always_true<T>(_: &T, _: &T) -> bool {
    true
}

// Plain real-body calls: no PFC assumptions or summary substitution can hide a bad fn pointer.
// One nondeterministic branch per wrapper; the common literal guard must be the only failure.
#[kani::proof]
#[kani::unwind(16)]
fn rejects_always_true() {
    let [a, b]: [u8; 2] = kani::any();
    let probe: u8 = kani::any();
    let case: u8 = kani::any_where(|c: &u8| *c < 3);
    match case {
        0 => {
            let mut v = [Cell::new(a), Cell::new(b)];
            kani::cover(true, "wrap invalid stable comparator reaches guard");
            // SAFETY: valid pair/scratch; only canonical identity is deliberately rejected.
            unsafe { stable_cell(v.as_mut_ptr(), &mut [], always_true::<Cell<u8>>, probe) };
        }
        1 => {
            let mut v = [a, b];
            kani::cover(true, "wrap invalid unstable comparator reaches guard");
            // SAFETY: valid pair; only canonical identity is deliberately rejected.
            unsafe { unstable_byte(v.as_mut_ptr(), always_true::<u8>, probe) };
        }
        _ => {
            let mut v = [NonCopyU8(a), NonCopyU8(b)];
            kani::cover(true, "wrap invalid Freeze comparator reaches guard");
            // SAFETY: valid pair; only canonical identity is deliberately rejected.
            unsafe { freeze_noncopy(v.as_mut_ptr(), always_true::<NonCopyU8>, probe) };
        }
    }
}

// Separate plain real trait execution, checked with the exact same model/count as the contracts.
// The mutation belongs only to this control, after the real entry returns, never to a wrapper.
#[kani::proof]
#[kani::unwind(16)]
fn rejects_payload_corruption() {
    let mut v: [u8; 2] = kani::any();
    let probe: u8 = kani::any();
    let before = count(&v, probe);
    let mut cmp: fn(&u8, &u8) -> bool = byte_less;
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(sorted(&v), "wrap control real body sorts keys");
    kani::assert(before == count(&v, probe), "wrap control real body keeps full values");
    kani::cover(true, "wrap payload corruption reached after real trait return");
    v[0] ^= 1;
    kani::assert(sorted(&v), "wrap corrupted payload keeps key order");
    kani::assert(before == count(&v, probe), "wrap full-value checker rejects payload corruption");
}
