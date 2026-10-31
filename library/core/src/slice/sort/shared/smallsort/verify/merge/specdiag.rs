//! Concrete specification diagnostics; selected explicitly, never ordinary suite entries.
//! Intentionally invalid memory controls must only execute in Kani.
//! Diagnostics of the removed raw helper contracts and predicates are retired (P1-CLEAN).
//! `kani::assert` keeps each literal message in the property description: `assert!` in core
//! reports a shared placeholder on the pinned Kani.

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
use super::{CopyOnDrop, set_value_probe};
use super::{Probe, VALUE_PROBE_BYTES, lt_u64, matches_value_probe};
use crate::cell::Cell;
use crate::mem::{MaybeUninit, align_of, offset_of, size_of};
#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
use crate::slice::sort::shared::smallsort::{bidirectional_merge, insert_tail};
use crate::slice::sort::shared::smallsort::{sort4_stable, swap_if_less};
use crate::{kani, ptr};

static READONLY_SOURCE: [u64; 4] = [6, 2, 4, 0];

#[repr(C)]
struct Pad {
    byte: u8,
    word: u32,
}

fn zero_probe() {
    // SAFETY: single-threaded diagnostic; no reference to the existing probe survives.
    unsafe { *ptr::addr_of_mut!(VALUE_PROBE_BYTES) = Probe([0; 128]) };
}

fn check_pad_layout() {
    kani::assert(size_of::<Pad>() == 8, "specdiag Pad size is eight");
    kani::assert(align_of::<Pad>() == 4, "specdiag Pad alignment is four");
    kani::assert(offset_of!(Pad, byte) == 0, "specdiag Pad byte offset is zero");
    kani::assert(offset_of!(Pad, word) == 4, "specdiag Pad word offset is four");
}

unsafe fn initialize_pad_fields(p: *mut Pad) {
    // SAFETY: caller supplies aligned allocated storage; write every field, no whole-Pad move.
    unsafe {
        ptr::write(ptr::addr_of_mut!((*p).byte), 0);
        ptr::write(ptr::addr_of_mut!((*p).word), 0);
    }
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(140)]
fn sort4_true_f_n4() {
    set_value_probe::<u64>();
    let src = [0u64; 4];
    let mut dst = [0u64; 4];
    let mut cmp = |_: &u64, _: &u64| true;
    kani::assert(
        CopyOnDrop::<u64>::valid_sort4_regions(src.as_ptr(), dst.as_mut_ptr()),
        "specdiag sort4 true F concrete requires",
    );
    kani::cover(true, "specdiag sort4 true F admission reached");
    // SAFETY: initialized disjoint regions; an unlawful order is the only negative factor.
    unsafe { sort4_stable(src.as_ptr(), dst.as_mut_ptr(), &mut cmp) };
    kani::cover(true, "specdiag sort4 true F checked call returned");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(140)]
fn insert_tail_true_f_n2() {
    set_value_probe::<u64>();
    let mut v = [0u64; 2];
    let begin = v.as_mut_ptr();
    // SAFETY: index one belongs to the two-element allocation.
    let tail = unsafe { begin.add(1) };
    let mut cmp = |_: &u64, _: &u64| true;
    kani::assert(
        CopyOnDrop::<u64>::valid_sorted_tail(begin, tail, &&mut cmp),
        "specdiag insert true F concrete requires",
    );
    kani::cover(true, "specdiag insert true F admission reached");
    // SAFETY: both elements initialized, sorted singleton prefix needs no comparison.
    unsafe { insert_tail(begin, tail, &mut cmp) };
    kani::cover(true, "specdiag insert true F checked call returned");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(140)]
fn merge_true_f_n2() {
    set_value_probe::<u64>();
    let v = [0u64; 2];
    let mut dst = [0u64; 2];
    let mut cmp = |_: &u64, _: &u64| true;
    kani::assert(v.len() >= 2 && v.len() <= 32, "specdiag merge true F length requires");
    kani::assert(
        CopyOnDrop::<u64>::valid_merge_destination(&v, dst.as_mut_ptr()),
        "specdiag merge true F destination requires",
    );
    kani::assert(
        CopyOnDrop::<u64>::merge_inputs_are_sorted(&v, &&mut cmp),
        "specdiag merge true F singleton halves requires",
    );
    kani::cover(true, "specdiag merge true F admission reached");
    // SAFETY: initialized disjoint regions and singleton halves.
    unsafe { bidirectional_merge(&v, dst.as_mut_ptr(), &mut cmp) };
    kani::cover(true, "specdiag merge true F checked call returned");
}

#[kani::proof]
#[kani::unwind(140)]
fn swap_fnmut_runtime_n2() {
    let mut v: [u64; 2] = kani::any();
    let calls = Cell::new(0u8);
    let mut cmp = |_: &u64, _: &u64| {
        calls.set(calls.get() + 1);
        false
    };
    // SAFETY: distinct initialized in-bounds positions.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    kani::assert(calls.get() == 1, "specdiag runtime FnMut observer calls exactly one");
    kani::cover(true, "specdiag runtime FnMut completion");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::swap_if_less)]
#[kani::unwind(140)]
fn swap_fnmut_contract_n2() {
    let mut v: [u64; 2] = kani::any();
    let calls = Cell::new(0u8);
    let mut cmp = |_: &u64, _: &u64| {
        calls.set(calls.get() + 1);
        false
    };
    kani::cover(true, "specdiag contract FnMut entry before checked call");
    // SAFETY: distinct initialized in-bounds positions; capture effect is under investigation.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    kani::cover(true, "specdiag contract FnMut checked call returned");
    kani::cover(calls.get() >= 2, "specdiag contract FnMut observer at least two calls");
    kani::cover(calls.get() == 3, "specdiag contract FnMut observer exactly three calls");
    kani::assert(calls.get() == 1, "specdiag contract FnMut observer calls exactly one");
}

#[kani::proof]
fn initialized_memory_positive() {
    let byte = 7u8;
    let word = 19u64;
    let flag = true;
    kani::assert(kani::mem::can_dereference(&byte), "specdiag initialized u8 dereference");
    kani::assert(kani::mem::can_dereference(&word), "specdiag initialized u64 dereference");
    kani::assert(kani::mem::can_dereference(&flag), "specdiag initialized bool dereference");
    // SAFETY: these three scalars are initialized, aligned and valid.
    unsafe {
        kani::assert(ptr::read_volatile(&byte) == 7, "specdiag initialized u8 value");
        kani::assert(ptr::read_volatile(&word) == 19, "specdiag initialized u64 value");
        kani::assert(ptr::read_volatile(&flag), "specdiag initialized bool value");
    }
    kani::cover(true, "specdiag initialized memory completion");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof]
#[kani::unwind(140)]
fn uninit_tail_predicate_admission() {
    let mut v = [MaybeUninit::<u64>::uninit(); 2];
    v[0].write(0);
    let begin = v.as_mut_ptr().cast::<u64>();
    // SAFETY: form a raw pointer only; do not read the uninitialized tail.
    let tail = unsafe { begin.add(1) };
    kani::assert(kani::mem::same_allocation(begin, tail), "specdiag tail admission allocation");
    kani::assert(begin.is_aligned() && tail.is_aligned(), "specdiag tail admission alignment");
    kani::assert(
        kani::mem::can_write(ptr::slice_from_raw_parts_mut(begin, 2)),
        "specdiag tail admission writable geometry",
    );
    let mut cmp = lt_u64;
    kani::assert(
        CopyOnDrop::<u64>::valid_sorted_tail(begin, tail, &&mut cmp),
        "specdiag uninitialized tail predicate admitted",
    );
    kani::cover(true, "specdiag uninitialized tail admission completion without tail read");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(140)]
fn uninit_tail_actual_pfc() {
    set_value_probe::<u64>();
    let mut v = [MaybeUninit::<u64>::uninit(); 2];
    v[0].write(0);
    let begin = v.as_mut_ptr().cast::<u64>();
    let mut cmp = lt_u64;
    kani::cover(true, "specdiag uninitialized tail before actual PFC");
    // SAFETY: intentionally violated; tail is allocated and aligned but uninitialized.
    unsafe { insert_tail(begin, begin.add(1), &mut cmp) };
    kani::cover(true, "specdiag uninitialized tail PFC returned");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof]
fn uninit_sort4_predicate_admission() {
    let src = [MaybeUninit::<u64>::uninit(); 4];
    let mut dst = [0u64; 4];
    let base = src.as_ptr().cast::<u64>();
    let out = dst.as_mut_ptr();
    kani::assert(base.is_aligned() && out.is_aligned(), "specdiag sort4 admission alignment");
    kani::assert(
        kani::mem::can_write(ptr::slice_from_raw_parts_mut(base.cast_mut(), 4)),
        "specdiag sort4 admission source geometry",
    );
    kani::assert(
        kani::mem::can_write(ptr::slice_from_raw_parts_mut(out, 4)),
        "specdiag sort4 admission destination geometry",
    );
    kani::assert(
        CopyOnDrop::<u64>::regions_are_disjoint(base, 4, out, 4),
        "specdiag sort4 admission disjoint allocations",
    );
    kani::assert(
        CopyOnDrop::<u64>::valid_sort4_regions(base, out),
        "specdiag uninitialized sort4 predicate admitted",
    );
    kani::cover(true, "specdiag uninitialized sort4 admission completion without source read");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(140)]
fn uninit_sort4_actual_pfc() {
    set_value_probe::<u64>();
    let src = [MaybeUninit::<u64>::uninit(); 4];
    let mut dst = [0u64; 4];
    let mut cmp = lt_u64;
    kani::cover(true, "specdiag uninitialized sort4 before actual PFC");
    // SAFETY: intentionally violated; source has geometry but no initialized elements.
    unsafe { sort4_stable(src.as_ptr().cast::<u64>(), dst.as_mut_ptr(), &mut cmp) };
    kani::cover(true, "specdiag uninitialized sort4 PFC returned");
}

#[kani::proof]
#[kani::unwind(140)]
fn readonly_sort4_source() {
    let mut dst = [0u64; 4];
    let mut cmp = lt_u64;
    // SAFETY: static source is readable/initialized; destination writable and disjoint.
    unsafe { sort4_stable(READONLY_SOURCE.as_ptr(), dst.as_mut_ptr(), &mut cmp) };
    kani::assert(!lt_u64(&dst[1], &dst[0]), "specdiag readonly sorted pair zero");
    kani::assert(!lt_u64(&dst[2], &dst[1]), "specdiag readonly sorted pair one");
    kani::assert(!lt_u64(&dst[3], &dst[2]), "specdiag readonly sorted pair two");
    kani::assert(dst[0] == 0, "specdiag readonly full value zero");
    kani::assert(dst[1] == 2, "specdiag readonly full value one");
    kani::assert(dst[2] == 4, "specdiag readonly full value two");
    kani::assert(dst[3] == 6, "specdiag readonly full value three");
    kani::cover(true, "specdiag readonly actual sort4 returned with full result");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof]
fn readonly_source_predicates() {
    let base = READONLY_SOURCE.as_ptr();
    let mut dst = [0u64; 4];
    kani::assert(
        kani::mem::can_write(ptr::slice_from_raw_parts_mut(base.cast_mut(), 4)),
        "specdiag readonly source can_write reports geometry",
    );
    kani::assert(
        CopyOnDrop::<u64>::valid_sort4_regions(base, dst.as_mut_ptr()),
        "specdiag readonly source valid_sort4_regions admitted",
    );
    kani::assert(
        kani::mem::can_dereference(ptr::slice_from_raw_parts(base, 4)),
        "specdiag readonly source can_dereference",
    );
    kani::cover(true, "specdiag readonly predicates completion without source write");
}

#[kani::proof]
#[kani::unwind(140)]
fn probe_t129_helper_oob() {
    zero_probe();
    let v = [0u8; 129];
    kani::cover(true, "specdiag probe t129 before actual helper");
    // SAFETY: intentionally violated; the actual helper reads byte 128 of the 128-byte probe.
    let matched = unsafe { matches_value_probe(&v) };
    kani::cover(matched, "specdiag probe t129 result matched");
    kani::cover(!matched, "specdiag probe t129 result differed");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(140)]
fn probe_t129_actual_contract() {
    zero_probe();
    let src = [[0u8; 129]; 4];
    let mut dst = [[0u8; 129]; 4];
    let mut cmp = |_: &[u8; 129], _: &[u8; 129]| false;
    kani::cover(true, "specdiag probe t129 before actual sort4 PFC");
    // SAFETY: real sort4 regions are initialized/disjoint; its count oracle is the negative.
    unsafe { sort4_stable(src.as_ptr(), dst.as_mut_ptr(), &mut cmp) };
    kani::cover(true, "specdiag probe t129 actual sort4 PFC returned");
}

#[kani::proof]
#[kani::unwind(140)]
fn padded_probe() {
    check_pad_layout();
    zero_probe();
    let mut slot = MaybeUninit::<Pad>::uninit();
    let p = slot.as_mut_ptr();
    // SAFETY: initialize all fields in their original allocation, leave padding untouched.
    unsafe { initialize_pad_fields(p) };
    kani::cover(true, "specdiag padded probe fields initialized before helper");
    // SAFETY: intentionally violated read; valid fields leave the padding bytes uninitialized.
    let matched = unsafe { matches_value_probe(p) };
    kani::cover(matched, "specdiag padded probe result matched");
    kani::cover(!matched, "specdiag padded probe result differed");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::swap_if_less)]
#[kani::unwind(140)]
fn padded_swap_actual_contract() {
    check_pad_layout();
    let mut slots = [const { MaybeUninit::<Pad>::uninit() }; 2];
    let base = slots.as_mut_ptr().cast::<Pad>();
    // SAFETY: both properly aligned slots exist; initialize fields without a whole-Pad move.
    unsafe {
        initialize_pad_fields(base);
        initialize_pad_fields(base.add(1));
    }
    let mut cmp = |_: &Pad, _: &Pad| false;
    kani::cover(true, "specdiag padded swap fields initialized before actual PFC");
    // SAFETY: valid Pad fields; investigate requires/snapshot first, nested same only if reached.
    unsafe { swap_if_less(base, 0, 1, &mut cmp) };
    kani::cover(true, "specdiag padded swap actual PFC returned");
}

#[kani::proof]
fn raw_uninit_read_sensitivity() {
    let slot = MaybeUninit::<u8>::uninit();
    kani::cover(true, "specdiag raw uninitialized before volatile read");
    // SAFETY: intentionally violated, with dependent observations retaining the actual read.
    let value = unsafe { ptr::read_volatile(slot.as_ptr()) };
    kani::cover(value == 0, "specdiag raw uninitialized read value zero");
    kani::cover(value != 0, "specdiag raw uninitialized read value nonzero");
}

#[kani::proof]
fn invalid_bool_sensitivity() {
    let byte = 2u8;
    let p = ptr::addr_of!(byte).cast::<bool>();
    kani::cover(true, "specdiag invalid bool initialized byte two before read");
    // SAFETY: intentionally violated value, distinct from an uninitialized-byte test.
    let value = unsafe { ptr::read_volatile(p) };
    kani::cover(value, "specdiag invalid bool read result true");
    kani::cover(!value, "specdiag invalid bool read result false");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::swap_if_less)]
#[kani::unwind(140)]
fn swap_t129_same_positive() {
    let mut v = [[0u8; 129]; 2];
    let mut cmp = |_: &[u8; 129], _: &[u8; 129]| false;
    // SAFETY: two initialized padding-free values; swap uses same, not the bounded probe.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    kani::cover(true, "specdiag swap t129 same positive completion");
}

#[cfg(any())] // retired by P1-CLEAN, see poneclean/DEACTIVATED.tsv
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::swap_if_less)]
#[kani::unwind(140)]
fn swap_u64_pure_pfc_positive() {
    let mut v: [u64; 2] = kani::any();
    let mut cmp = |_: &u64, _: &u64| false;
    // SAFETY: initialized distinct in-bounds positions and a pure comparator.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    kani::cover(true, "specdiag swap u64 pure PFC positive completion");
}
