//! Full-value witnesses and native counts for concrete, padding-free element types.

use super::{
    PROBE_BYTES, Probe, SMALL_SORT_GENERAL_SCRATCH_LEN, StableSmallSortTypeImpl, VALUE_PROBE_BYTES,
    assert_sorted_and_probe_preserved, lt_u8, lt_u64, matches_value_probe,
};
use crate::mem::MaybeUninit;
use crate::{kani, ptr};

fn project_u64(p: u64, mut bytes: [u8; PROBE_BYTES]) {
    let value_bytes = p.to_ne_bytes();
    bytes[..8].copy_from_slice(&value_bytes);
    // SAFETY: single-threaded harness; no reference to the static is alive.
    unsafe { *ptr::addr_of_mut!(VALUE_PROBE_BYTES) = Probe(bytes) };
}

fn project_u8(p: u8, mut bytes: [u8; PROBE_BYTES]) {
    bytes[0] = p;
    // SAFETY: single-threaded harness; no reference to the static is alive.
    unsafe { *ptr::addr_of_mut!(VALUE_PROBE_BYTES) = Probe(bytes) };
}

fn set_typed_probe_u64(p: u64) {
    project_u64(p, [0; PROBE_BYTES]);
}

fn set_typed_probe_u8(p: u8) {
    project_u8(p, [0; PROBE_BYTES]);
}

macro_rules! count_steps {
    ($values:ident, $p:ident, $count:ident, $n:ident; $($i:literal)*) => {$(
        if $i < $n && $values[$i] == $p {
            $count += 1;
        }
    )*};
}

macro_rules! define_native_checker {
    ($count:ident, $check:ident, $t:ty) => {
        fn $count<const N: usize>(values: &[$t; N], p: $t) -> usize {
            const { assert!(N <= 32) };
            let mut count = 0;
            count_steps!(values, p, count, N;
                0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
                16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
            );
            count
        }

        fn $check<F: FnMut(&$t, &$t) -> bool, const N: usize>(
            orig: &[$t; N],
            out: &[$t; N],
            p: $t,
            cmp: &mut F,
        ) {
            for i in 1..N {
                assert!(!cmp(&out[i], &out[i - 1]), "output is sorted");
            }
            assert!(
                $count(orig, p) == $count(out, p),
                "typed full-value counts are preserved"
            );
        }
    };
}

define_native_checker!(count_u64, assert_u64_properties, u64);
define_native_checker!(count_u8, assert_u8_properties, u8);

#[kani::proof]
#[kani::unwind(34)]
fn probe_bridge_u64_u8() {
    let x64: u64 = kani::any();
    let p64: u64 = kani::any();
    // Arbitrary unused suffix: matches_value_probe::<u64> observes exactly bytes 0..8.
    project_u64(p64, kani::any());
    // SAFETY: x64 is initialized, readable and has no padding; the probe holds 128 bytes.
    assert!(unsafe { matches_value_probe::<u64>(&x64) } == (x64 == p64));

    let x8: u8 = kani::any();
    let p8: u8 = kani::any();
    // The u64 phase has ended; this phase observes only the u8 probe's first byte.
    project_u8(p8, kani::any());
    // SAFETY: x8 is one initialized, readable byte; the probe holds 128 bytes.
    assert!(unsafe { matches_value_probe::<u8>(&x8) } == (x8 == p8));
    kani::cover(true, "typed probe bridge completes for both types");
}

#[kani::proof]
#[kani::unwind(34)]
fn general_u64_n8_projected_generic() {
    let p: u64 = kani::any();
    set_typed_probe_u64(p);
    let mut v: [u64; 8] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    super::super::super::small_sort_general(&mut v, &mut cmp);
    assert_sorted_and_probe_preserved::<u64, _, 8>(&orig, &v, &mut cmp);
    kani::cover(true, "general direct split properties checked");
}

#[kani::proof]
#[kani::unwind(34)]
fn general_u64_n8_native() {
    let p: u64 = kani::any();
    set_typed_probe_u64(p);
    let mut v: [u64; 8] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    super::super::super::small_sort_general(&mut v, &mut cmp);
    assert_u64_properties(&orig, &v, p, &mut cmp);
    kani::cover(true, "general direct split properties checked");
}

#[kani::proof]
#[kani::unwind(34)]
fn stable_u64_n8_native() {
    let p: u64 = kani::any();
    set_typed_probe_u64(p);
    let mut v: [u64; 8] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    let mut scratch = [const { MaybeUninit::<u64>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN];
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    assert_u64_properties(&orig, &v, p, &mut cmp);
    kani::cover(true, "stable direct split properties checked");
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn merge_u64_n13_projected_actual_pfc() {
    let p: u64 = kani::any();
    set_typed_probe_u64(p);
    let v: [u64; 13] = kani::any();
    let mut dst = MaybeUninit::<[u64; 13]>::uninit();
    let mut cmp = lt_u64;
    // SAFETY: the actual callee's original contract is checked by proof_for_contract.
    unsafe {
        crate::slice::sort::shared::smallsort::bidirectional_merge(
            &v,
            dst.as_mut_ptr() as *mut u64,
            &mut cmp,
        )
    };
    kani::cover(true, "merge returns for a permitted length");
}

#[kani::proof]
#[kani::unwind(34)]
fn value_corruption_control_u64_n2() {
    let p: u64 = kani::any();
    set_typed_probe_u64(p);
    let mut v: [u64; 2] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    super::super::super::small_sort_general(&mut v, &mut cmp);
    // The low bit is payload under lt_u64; sortedness survives this mutation.
    v[0] ^= 1;
    kani::cover(true, "general sort returns and payload is flipped before typed checks");
    assert_u64_properties(&orig, &v, p, &mut cmp);
}

#[kani::proof]
#[kani::unwind(34)]
fn general_u8_n9_native() {
    let p: u8 = kani::any();
    set_typed_probe_u8(p);
    let mut v: [u8; 9] = kani::any();
    let orig = v;
    let mut cmp = lt_u8;
    super::super::super::small_sort_general(&mut v, &mut cmp);
    assert_u8_properties(&orig, &v, p, &mut cmp);
    kani::cover(true, "general route properties checked");
}

#[kani::proof]
#[kani::unwind(34)]
fn value_corruption_control_u8_n2() {
    let p: u8 = kani::any();
    set_typed_probe_u8(p);
    let mut v: [u8; 2] = kani::any();
    let orig = v;
    let mut cmp = lt_u8;
    super::super::super::small_sort_general(&mut v, &mut cmp);
    // The low bit is payload under lt_u8; sortedness survives this mutation.
    v[0] ^= 1;
    kani::cover(true, "general sort returns and payload is flipped before typed checks");
    assert_u8_properties(&orig, &v, p, &mut cmp);
}
