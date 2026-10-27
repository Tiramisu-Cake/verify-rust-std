//! Wave 3 L1u diagnostics. No verified-contract stubs or should_panic.
//! The U1 harnesses require a separate diagnostic run with -Z uninit-checks;
//! compiling them without that flag establishes no uninitialized-read evidence.

use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
use crate::{mem::MaybeUninit, ptr};

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

fn zst_stable<const N: usize>() {
    let mut v = [(); N];
    let mut scratch = [MaybeUninit::<()>::uninit(); 48];
    <() as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut reading_less);
}

fn zst_network<const N: usize>() {
    let mut v = [(); N];
    <() as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut reading_less);
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

#[kani::proof]
fn z1_volatile_unit() {
    let value = ();
    // SAFETY: a reference to an initialized, aligned ZST.
    unsafe { ptr::read_volatile(&value); }
    kani::cover(true, "Z1 volatile unit read returned");
}

#[kani::proof]
fn z1_sort4_unit() {
    let v = [(); 4];
    let mut dst = [MaybeUninit::<()>::uninit(); 4];
    // SAFETY: separate source/destination arrays, each with four elements.
    unsafe { super::super::sort4_stable(v.as_ptr(), dst.as_mut_ptr().cast(), &mut reading_less); }
    kani::cover(true, "Z1 sort4 unit returned");
}

#[kani::proof]
fn z1_swap_unit() {
    let mut v = [(); 2];
    // SAFETY: distinct in-bounds indices in the same array.
    unsafe { super::super::swap_if_less(v.as_mut_ptr(), 0, 1, &mut reading_less); }
    kani::cover(true, "Z1 swap unit returned");
}

// U1: explicit stable scratch lets the comparator witness a real scratch read,
// rather than merely reaching the allocation or a write to the scratch buffer.
fn uninit_general<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    let mut scratch = [MaybeUninit::<u64>::uninit(); 48];
    let start = scratch.as_ptr() as usize;
    let end = start + crate::mem::size_of_val(&scratch);
    let mut read_scratch = false;
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut |a, b| {
        let ap = a as *const u64 as usize;
        let bp = b as *const u64 as usize;
        let result = reading_less(a, b);
        read_scratch |= (start <= ap && ap < end) || (start <= bp && bp < end);
        result
    });
    kani::cover(read_scratch, "U1 general: comparator read initialized scratch");
    kani::cover(true, "U1 general: normal return");
}

fn uninit_network<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut reading_less);
    // For these constant lengths N >= 18, the real network body cannot return
    // via no_merge: a normal return follows the scratch -> v copy at smallsort.rs:369.
    // This is a control-flow witness of that read, not an instrumented load cover.
    kani::cover(true, "U1 network: returned after scratch copy (N >= 18)");
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

uninit_case!(u1_general_8, uninit_general, 8);
uninit_case!(u1_general_16, uninit_general, 16);
uninit_case!(u1_general_32, uninit_general, 32);
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
