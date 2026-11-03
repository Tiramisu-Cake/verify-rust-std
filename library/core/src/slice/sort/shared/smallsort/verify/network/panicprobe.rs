//! PANICPROBE: which default checks fail on the paths the `panic_on_ord_violation` stub of the
//! safety roots cuts. Opt-in only; no stubs. Roots 1 and 2 calibrate `#[kani::should_panic]` on
//! the pin (a panic alone, then a panic mixed with an out-of-bounds read). Roots 3 to 6 run the
//! real unstable network (u8, N18) and stable general (u8, N16) bodies with an arbitrary boolean
//! comparator that reads no memory, each once with and once without `should_panic`.

use crate::kani;
use crate::mem::MaybeUninit;
use crate::slice::sort::shared::smallsort::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};

/// Arbitrary result on every call; reads neither argument and mutates nothing.
fn any_less(_a: &u8, _b: &u8) -> bool {
    kani::any()
}

/// Unstable dispatch for u8 at N18: `small_sort_network` with one `bidirectional_merge` of 18.
fn network_u8_n18() {
    let mut v: [u8; 18] = kani::any();
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut any_less);
    kani::cover(true, "panicprobe network u8 n18 normal return");
}

/// Stable dispatch for u8 at N16: `small_sort_general_with_scratch`, two `sort8_stable` merges of
/// 8 and one `bidirectional_merge` of 16.
fn general_u8_n16() {
    let mut v: [u8; 16] = kani::any();
    let mut scratch = [const { MaybeUninit::<u8>::uninit() }; 48];
    <u8 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut any_less);
    kani::cover(true, "panicprobe general u8 n16 normal return");
}

#[kani::proof]
#[kani::should_panic]
#[kani::unwind(65)]
fn panic_control_plain() {
    if kani::any() {
        panic!("panicprobe control");
    }
    kani::cover(true, "panicprobe control normal return");
}

#[kani::proof]
#[kani::should_panic]
#[kani::unwind(65)]
fn panic_control_ub() {
    let local: [u8; 4] = kani::any();
    if kani::any() {
        panic!("panicprobe ub control");
    }
    if kani::any() {
        let past_end = local.as_ptr().wrapping_add(local.len());
        // SAFETY: none. Deliberate out-of-bounds read one past the local array, Kani only; the
        // value is used so the read stays in the program.
        let byte = unsafe { *past_end };
        crate::hint::black_box(byte);
    }
    kani::cover(true, "panicprobe ub control normal return");
}

#[kani::proof]
#[kani::should_panic]
#[kani::unwind(65)]
fn panic_network_u8_n18_should_panic() {
    network_u8_n18();
}

#[kani::proof]
#[kani::unwind(65)]
fn panic_network_u8_n18_plain() {
    network_u8_n18();
}

#[kani::proof]
#[kani::should_panic]
#[kani::unwind(65)]
fn panic_general_u8_n16_should_panic() {
    general_u8_n16();
}

#[kani::proof]
#[kani::unwind(65)]
fn panic_general_u8_n16_plain() {
    general_u8_n16();
}
