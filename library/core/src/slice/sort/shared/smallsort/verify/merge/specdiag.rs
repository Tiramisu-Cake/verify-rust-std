//! Concrete specification diagnostics; selected explicitly, never ordinary suite entries.
//! Intentionally invalid memory controls must only execute in Kani.
//! `kani::assert` keeps each literal message in the property description: `assert!` in core
//! reports a shared placeholder on the pinned Kani.

use super::{Probe, VALUE_PROBE_BYTES, lt_u64, matches_value_probe};
use crate::cell::Cell;
use crate::mem::{MaybeUninit, align_of, offset_of, size_of};
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
