//! Wave 3 L1u diagnostics. No verified-contract stubs or should_panic.
//! The U1 harnesses require a separate diagnostic run with -Z uninit-checks;
//! compiling them without that flag establishes no uninitialized-read evidence.
//! The U1 negative controls go only into requests with `"uninit_checks": true`:
//! without the flag they return SUCCESS and say nothing (R9 ffd4250d, F6).

use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
use crate::kani;
use crate::mem::{ManuallyDrop, MaybeUninit};
use crate::ptr;

// Variant A (R6 section 2): cut only the explicit order-violation panic.
// Normal-return covers in the callers rule out a wholly cut proof.
fn cut_ord_violation() -> ! {
    kani::assume(false);
    unreachable!()
}

fn reading_less<T: Copy>(a: &T, b: &T) -> bool {
    // SAFETY: the sort must supply initialized, readable comparator arguments.
    unsafe {
        let _left = ptr::read_volatile(a);
        let _right = ptr::read_volatile(b);
    }
    kani::any()
}

// Z1 with literal inputs: `[(); N]`, a `Copy` scratch array and a plain volatile comparator.
fn zst_stable<const N: usize>() {
    let mut v = [(); N];
    let mut scratch = [MaybeUninit::<()>::uninit(); 48];
    <() as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut reading_less);
}

fn zst_network<const N: usize>() {
    let mut v = [(); N];
    <() as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut reading_less);
}

// Z1 with the job 85 inputs at a fixed length (R9 F1): `array::from_fn`, a `const`-block scratch
// and the `ManuallyDrop` volatile comparator of `network::w2_reading_less`. Only the symbolic
// length (`any_where` + `match`) of `network::w2_k16_zst_stable` is left out.
fn w2_like_less<T>(a: &T, b: &T) -> bool {
    // SAFETY: as `reading_less`; ManuallyDrop keeps the duplicate from being dropped.
    unsafe {
        let _left = ManuallyDrop::new(ptr::read_volatile(a));
        let _right = ManuallyDrop::new(ptr::read_volatile(b));
    }
    kani::any()
}

fn zst_stable_w2<const N: usize>() {
    let mut v: [(); N] = crate::array::from_fn(|_| ());
    let mut scratch = [const { MaybeUninit::<()>::uninit() }; 48];
    <() as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut w2_like_less::<()>);
}

fn zst_from_fn<const N: usize>() {
    // R9 N2: no read of the result, so this isolates `from_fn` from `z1_volatile_unit`.
    let v: [(); N] = crate::array::from_fn(|_| ());
    kani::cover(v.len() == N, "Z1 from_fn unit: array of length N built");
}

macro_rules! zst_case {
    ($name:ident, $route:ident, $n:literal) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
        #[kani::unwind(65)]
        fn $name() {
            $route::<$n>();
            kani::cover(true, concat!("Z1 normal return: ", stringify!($route), " N=", stringify!($n)));
        }
    };
}

zst_case!(z1_stable_0, zst_stable, 0);
zst_case!(z1_stable_1, zst_stable, 1);
zst_case!(z1_stable_2, zst_stable, 2);
zst_case!(z1_stable_7, zst_stable, 7);
zst_case!(z1_stable_8, zst_stable, 8);
zst_case!(z1_stable_15, zst_stable, 15);
zst_case!(z1_stable_16, zst_stable, 16);
zst_case!(z1_stable_17, zst_stable, 17);
zst_case!(z1_stable_31, zst_stable, 31);
zst_case!(z1_stable_32, zst_stable, 32);
zst_case!(z1_network_8, zst_network, 8);
zst_case!(z1_network_9, zst_network, 9);
zst_case!(z1_network_12, zst_network, 12);
zst_case!(z1_network_13, zst_network, 13);
zst_case!(z1_network_17, zst_network, 17);
zst_case!(z1f_stable_2, zst_stable_w2, 2);
zst_case!(z1f_stable_8, zst_stable_w2, 8);
zst_case!(z1f_stable_16, zst_stable_w2, 16);
zst_case!(z1f_stable_32, zst_stable_w2, 32);
zst_case!(z1_from_fn_unit_2, zst_from_fn, 2);
zst_case!(z1_from_fn_unit_32, zst_from_fn, 32);
// R9 Z-a: odd lengths and the len < 2 early return with the job 85 inputs.
zst_case!(z1f_stable_1, zst_stable_w2, 1);
zst_case!(z1f_stable_7, zst_stable_w2, 7);
zst_case!(z1f_stable_17, zst_stable_w2, 17);
zst_case!(z1f_stable_31, zst_stable_w2, 31);

#[kani::proof]
fn z1_volatile_unit() {
    let value = ();
    // SAFETY: a reference to an initialized, aligned ZST.
    let _ = unsafe { ptr::read_volatile(&value) };
    kani::cover(true, "Z1 volatile unit read returned");
}

#[kani::proof]
fn z1_sort4_unit() {
    let v = [(); 4];
    let mut dst = [MaybeUninit::<()>::uninit(); 4];
    // SAFETY: separate source/destination arrays, each with four elements.
    unsafe { super::super::sort4_stable(v.as_ptr(), dst.as_mut_ptr().cast(), &mut reading_less) };
    kani::cover(true, "Z1 sort4 unit returned");
}

#[kani::proof]
fn z1_swap_unit() {
    let mut v = [(); 2];
    // SAFETY: distinct in-bounds indices in the same array.
    unsafe { super::super::swap_if_less(v.as_mut_ptr(), 0, 1, &mut reading_less) };
    kani::cover(true, "Z1 swap unit returned");
}

// R9 F5: the remaining primitives of the stable path for N = 2..7.
#[kani::proof]
fn z1_copy_unit() {
    let v = [(); 2];
    let mut scratch = [MaybeUninit::<()>::uninit(); 2];
    // SAFETY: as small_sort_general_with_scratch for len < 8: one element into separate scratch.
    unsafe { ptr::copy_nonoverlapping(v.as_ptr(), scratch.as_mut_ptr().cast::<()>(), 1) };
    kani::cover(true, "Z1 copy unit returned");
}

#[kani::proof]
#[kani::unwind(5)]
fn z1_merge2_unit() {
    let v = [(); 2];
    let mut dst = [MaybeUninit::<()>::uninit(); 2];
    // SAFETY: len 2 >= 2, `dst` is separate and valid for two writes. The order-violation panic
    // is not stubbed here: if it were reachable, the harness would fail on it.
    unsafe { super::super::bidirectional_merge(&v, dst.as_mut_ptr().cast::<()>(), &mut reading_less) };
    kani::cover(true, "Z1 merge2 unit returned");
}

// R9 Z-a: odd length, the last_src copy of bidirectional_merge (smallsort.rs:931).
#[kani::proof]
#[kani::unwind(5)]
fn z1_merge3_unit() {
    let v = [(); 3];
    let mut dst = [MaybeUninit::<()>::uninit(); 3];
    // SAFETY: len 3 >= 2, `dst` is separate and valid for three writes.
    unsafe { super::super::bidirectional_merge(&v, dst.as_mut_ptr().cast::<()>(), &mut reading_less) };
    kani::cover(true, "Z1 merge3 unit returned");
}

#[kani::proof]
#[kani::unwind(5)]
fn z1_insert_tail_unit() {
    let mut v = [(); 2];
    let base = v.as_mut_ptr();
    // SAFETY: begin < tail in the same array, both initialized.
    unsafe { super::super::insert_tail(base, base.add(1), &mut reading_less) };
    kani::cover(true, "Z1 insert_tail unit returned");
}

// U1: explicit stable scratch lets the comparator witness a real scratch read,
// rather than merely reaching the allocation or a write to the scratch buffer.
// After the sort every element of `v` is read (R9 F2), so a scratch -> v copy that only
// carried uninitialized state forward fails here rather than vanishing.
fn read_all<const N: usize>(v: &[u64; N]) {
    for i in 0..N {
        // SAFETY: `i < N`, in bounds of `v`.
        let _ = unsafe { ptr::read_volatile(v.as_ptr().add(i)) };
    }
}

fn uninit_general<const N: usize>(scratch: &mut [MaybeUninit<u64>; 48]) {
    let mut v: [u64; N] = kani::any();
    let start = scratch.as_ptr() as usize;
    let end = start + crate::mem::size_of_val(&*scratch);
    let mut read_scratch = false;
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, scratch, &mut |a, b| {
        let ap = a as *const u64 as usize;
        let bp = b as *const u64 as usize;
        let result = reading_less(a, b);
        read_scratch |= (start <= ap && ap < end) || (start <= bp && bp < end);
        result
    });
    kani::cover(read_scratch, "U1 general: comparator read initialized scratch");
    read_all(&v);
    kani::cover(true, "U1 general: normal return, v read back");
}

fn uninit_general_only<const N: usize>() {
    let mut scratch = [MaybeUninit::<u64>::uninit(); 48];
    uninit_general::<N>(&mut scratch);
}

fn uninit_network<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut reading_less);
    // For these constant lengths N >= 18, the real network body cannot return
    // via no_merge: a normal return follows the scratch -> v copy at smallsort.rs:369.
    // Reading all of `v` afterwards turns that copy into a checked read.
    read_all(&v);
    kani::cover(true, "U1 network: v read back after scratch copy (N >= 18)");
}

macro_rules! uninit_case {
    ($name:ident, $route:ident, $n:literal) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
        #[kani::unwind(65)]
        fn $name() {
            $route::<$n>();
        }
    };
}

uninit_case!(u1_general_8, uninit_general_only, 8);
uninit_case!(u1_general_16, uninit_general_only, 16);
uninit_case!(u1_general_32, uninit_general_only, 32);
// N=8 and N=16 are not network scratch-read paths (no_merge).
uninit_case!(u1_network_18, uninit_network, 18);
uninit_case!(u1_network_32, uninit_network, 32);

#[kani::proof]
fn u1_initialized_control() {
    let cell = MaybeUninit::new(kani::any::<u64>());
    // SAFETY: initialized by MaybeUninit::new above.
    let _value = unsafe { ptr::read_volatile(cell.as_ptr()) };
    kani::cover(true, "U1 initialized control: read returned");
}

// Deliberate negative control. Select only in the separate U1 diagnostic run;
// it must not be included in the final normal CI proof set.
#[kani::proof]
fn u1_uninitialized_control() {
    let cell = MaybeUninit::<u64>::uninit();
    kani::cover(true, "U1 negative control: before uninitialized read");
    // Deliberate UB: this read must be detected by -Z uninit-checks.
    let _value = unsafe { ptr::read_volatile(cell.as_ptr()) };
}

// R9 F3, general layout: after the real sort at N = 8, scratch cells 8..47 are never written
// (sort4_stable fills 0..8, the merge reads them back). The negative reads cell 47 untouched;
// the paired positive writes that same cell first.
// WRITE: 0 leaves the cell alone, 1 writes it through `MaybeUninit::write`, 2 through a raw
// `*mut u64` as the sort's own copies do (R9 N1).
fn uninit_general_tail<const WRITE: u8>() {
    let mut scratch = [MaybeUninit::<u64>::uninit(); 48];
    uninit_general::<8>(&mut scratch);
    if WRITE == 1 {
        let _ = scratch[47].write(kani::any());
    } else if WRITE == 2 {
        // SAFETY: cell 47 is in bounds of `scratch`.
        unsafe { scratch.as_mut_ptr().add(47).cast::<u64>().write(kani::any()) };
    }
    kani::cover(true, "U1 general tail: before reading scratch[47]");
    // SAFETY: in bounds; initialized unless WRITE == 0 (the negative control's deliberate UB).
    let _ = unsafe { ptr::read_volatile(scratch.as_ptr().add(47).cast::<u64>()) };
    kani::cover(true, "U1 general tail: read returned");
}

#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
#[kani::unwind(65)]
fn u1_general_8_tail_uninit() {
    uninit_general_tail::<0>();
}

#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
#[kani::unwind(65)]
fn u1_general_8_tail_written() {
    uninit_general_tail::<1>();
}

#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
#[kani::unwind(65)]
fn u1_general_8_tail_written_raw() {
    uninit_general_tail::<2>();
}

// R9 F3, network layout: `MaybeUninit<[u64; 32]>` reached through a cast pointer, as
// small_sort_network's stack_array. A merge at N = 18 writes cells 0..17; cell 31 stays
// uninitialized. This is the union-pointee risk of the task.
fn uninit_network_tail<const WRITE: bool>() {
    let mut stack_array = MaybeUninit::<[u64; 32]>::uninit();
    let base = stack_array.as_mut_ptr() as *mut u64;
    // SAFETY: all offsets are below 32, in bounds of `stack_array`.
    unsafe {
        for i in 0..18 {
            base.add(i).write(kani::any());
        }
        if WRITE {
            base.add(31).write(kani::any());
        }
    }
    kani::cover(true, "U1 network tail: before reading cell 31");
    // SAFETY: in bounds; initialized only when WRITE (the negative control's deliberate UB).
    let _ = unsafe { ptr::read_volatile(base.add(31)) };
    kani::cover(true, "U1 network tail: read returned");
}

#[kani::proof]
#[kani::unwind(20)]
fn u1_network_layout_tail_uninit() {
    uninit_network_tail::<false>();
}

#[kani::proof]
#[kani::unwind(20)]
fn u1_network_layout_tail_written() {
    uninit_network_tail::<true>();
}
