//! Opt-in diagnostic for `-Z valid-value-checks`; outside the ordinary v7 suite.
//! The negative controls deliberately create invalid scalar values. Real routes use
//! valid inputs and strict order, execute real bodies, and assert no sort properties.

use super::super::{
    SMALL_SORT_GENERAL_SCRATCH_LEN, StableSmallSortTypeImpl, UnstableSmallSortTypeImpl,
};
use crate::kani;
use crate::mem::MaybeUninit;
use crate::num::NonZeroU8;
use crate::ptr;

// Each pair uses the same load, with live, initialized, correctly aligned storage.
// SAFETY for callers: byte must be 0 or 1; the negative control violates only this.
unsafe fn load_bool(byte: u8) -> bool {
    unsafe { ptr::read((&byte as *const u8).cast::<bool>()) }
}

// SAFETY for callers: scalar must be a Unicode scalar value. The u32 backing
// storage also supplies char's alignment; the negative control uses a surrogate.
unsafe fn load_char(scalar: u32) -> char {
    unsafe { ptr::read((&scalar as *const u32).cast::<char>()) }
}

#[kani::proof]
#[kani::unwind(16)]
fn rejects_bool_byte_2() {
    // INTENTIONAL UB: calibration must fail a located value-validity check.
    let value = unsafe { load_bool(2u8) };
    kani::cover(value, "invalid bool load result is consumed");
}

#[kani::proof]
#[kani::unwind(16)]
fn accepts_bool_byte_0_or_1() {
    let byte: u8 = kani::any();
    kani::assume(byte <= 1);
    // SAFETY: the assumed domain contains exactly bool's two representations.
    let value = unsafe { load_bool(byte) };
    kani::cover(!value, "valid bool byte 0 returns");
    kani::cover(value, "valid bool byte 1 returns");
}

#[kani::proof]
#[kani::unwind(16)]
fn rejects_char_surrogate() {
    // INTENTIONAL UB: 0xD800 is not a Unicode scalar value.
    let value = unsafe { load_char(0xD800u32) };
    kani::cover(value as u32 == 0xD800, "invalid char load result is consumed");
}

#[kani::proof]
#[kani::unwind(16)]
fn accepts_char_scalar() {
    let scalar: u32 = kani::any();
    kani::assume(scalar <= 0x10FFFF && (scalar < 0xD800 || scalar > 0xDFFF));
    // SAFETY: the assumed domain is exactly the Unicode scalar values.
    let value = unsafe { load_char(scalar) };
    kani::cover(value as u32 == 0, "valid char lower endpoint returns");
    kani::cover(value as u32 == 0x10FFFF, "valid char upper endpoint returns");
    kani::cover(value as u32 == 0xD7FF, "valid char below surrogate gap returns");
    kani::cover(value as u32 == 0xE000, "valid char above surrogate gap returns");
}

#[kani::proof]
#[kani::solver(cadical)]
#[kani::unwind(20)]
fn unstable_bool_n4_to8() {
    let mut values: [bool; 8] = kani::any();
    let len: usize = kani::any();
    kani::assume(len >= 4 && len <= 8);
    let reversed = values[0] && !values[1];
    // Freeze + Copy, size 1: the network route. At N4..8 that route uses
    // insertion from index 1, without sort9/sort13 or its scratch merge.
    <bool as UnstableSmallSortTypeImpl>::small_sort(
        &mut values[..len],
        &mut |a: &bool, b: &bool| *a < *b,
    );
    kani::cover(len == 4, "validval unstable bool network route N4 returns");
    kani::cover(len == 5, "validval unstable bool network route N5 returns");
    kani::cover(len == 6, "validval unstable bool network route N6 returns");
    kani::cover(len == 7, "validval unstable bool network route N7 returns");
    kani::cover(len == 8, "validval unstable bool network route N8 returns");
    kani::cover(reversed, "validval unstable bool reversed input returns");
}

// Fixed-length counterparts of unstable_bool_n4_to8, with the same strict
// comparator and post-call route/reversed-input covers. N2 and N4 both select
// the network entry's insertion body from index 1, without scratch merge.
#[kani::proof]
#[kani::solver(cadical)]
#[kani::unwind(20)]
fn unstable_bool_n2() {
    let mut values: [bool; 2] = kani::any();
    let reversed = values[0] && !values[1];
    <bool as UnstableSmallSortTypeImpl>::small_sort(
        &mut values,
        &mut |a: &bool, b: &bool| *a < *b,
    );
    kani::cover(true, "validval unstable bool network route N2 returns");
    kani::cover(reversed, "validval unstable bool reversed input returns");
}

#[kani::proof]
#[kani::solver(cadical)]
#[kani::unwind(20)]
fn unstable_bool_n4() {
    let mut values: [bool; 4] = kani::any();
    let reversed = values[0] && !values[1];
    <bool as UnstableSmallSortTypeImpl>::small_sort(
        &mut values,
        &mut |a: &bool, b: &bool| *a < *b,
    );
    kani::cover(true, "validval unstable bool network route N4 returns");
    kani::cover(reversed, "validval unstable bool reversed input returns");
}

fn valid_char() -> char {
    let scalar: u32 = kani::any();
    kani::assume(scalar <= 0x10FFFF && (scalar < 0xD800 || scalar > 0xDFFF));
    char::from_u32(scalar).unwrap()
}

#[kani::proof]
#[kani::solver(cadical)]
#[kani::unwind(20)]
fn stable_char_n4() {
    let mut values: [char; 4] = crate::array::from_fn(|_| valid_char());
    let reversed = values[0] > values[1];
    let mut scratch = [const { MaybeUninit::<char>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN];
    <char as StableSmallSortTypeImpl>::small_sort(
        &mut values,
        &mut scratch,
        &mut |a: &char, b: &char| *a < *b,
    );
    kani::cover(true, "validval stable char general scratch route N4 returns");
    kani::cover(reversed, "validval stable char reversed input returns");
}

#[kani::proof]
#[kani::solver(cadical)]
#[kani::unwind(20)]
fn unstable_nonzero_u8_n4() {
    let mut values: [NonZeroU8; 4] = crate::array::from_fn(|_| {
        let byte: u8 = kani::any();
        kani::assume(byte != 0);
        NonZeroU8::new(byte).unwrap()
    });
    let reversed = values[0].get() > values[1].get();
    <NonZeroU8 as UnstableSmallSortTypeImpl>::small_sort(
        &mut values,
        &mut |a: &NonZeroU8, b: &NonZeroU8| a.get() < b.get(),
    );
    kani::cover(true, "validval unstable NonZeroU8 network route N4 returns");
    kani::cover(reversed, "validval unstable NonZeroU8 reversed input returns");
}
