//! S3-1 bounded actual-body PFCs. No assumed callee or panic stub is used here.
//! Full independent bytes, concrete u8/KeyLess<u8>, normal-return correctness.
//! Backing sizes/offsets below are part of the claim; no allocation lifting.
use super::super::{swap_if_less, sort4_stable, insert_tail, bidirectional_merge};
use super::sorting_model::{KeyLess, enabled, snapshot, post};
use super::{sorting_s2_span as span, sorting_s2_swap as pair};
use crate::{kani, mem::MaybeUninit, slice};

fn active() -> bool {
    enabled::<u8, KeyLess<u8>>() && span::active::<u8, KeyLess<u8>>()
        && pair::enabled::<u8, KeyLess<u8>>()
}
fn ordered(v: &[u8]) -> bool {
    let mut i = 1;
    while i < v.len() {
        if v[i] < v[i - 1] { return false; }
        i += 1;
    }
    true
}

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(36)]
fn s3_swap_u8_geometry() {
    kani::assert(active(), "S3_SWAP_ACTIVE");
    let mut v: [u8; 34] = kani::any();
    let before = v;
    let base: usize = kani::any();
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(base <= 20 && a < 13 && b < 13);
    let p = unsafe { v.as_mut_ptr().add(base) };
    let pre = pair::capture::<u8, KeyLess<u8>>(p, a, b);
    unsafe { swap_if_less(p, a, b, &mut KeyLess::<u8>::new()) };
    kani::assert(pair::post::<u8, KeyLess<u8>>(pre, p, a, b), "S3_SWAP_EXACT_TRANSFER");
    for i in 0..34 {
        kani::assert(i == base + a || i == base + b || v[i] == before[i], "S3_SWAP_FULL_FRAME");
    }
    kani::cover(a == b, "S3_SWAP_EQUAL");
    kani::cover(a < b && before[base + b] < before[base + a], "S3_SWAP_TAKEN");
    kani::cover(a > b && before[base + b] >= before[base + a], "S3_SWAP_REVERSE_UNTAKEN");
    kani::cover(a != b && before[base + a] == before[base + b], "S3_SWAP_DUPLICATE");
    kani::cover(base == 0, "S3_SWAP_BASE_ZERO");
    kani::cover(base == 20, "S3_SWAP_BASE_LAST");
    kani::cover(true, "S3_SWAP_USEFUL_RETURN");
}

#[kani::proof_for_contract(sort4_stable)]
#[kani::unwind(8)]
fn s3_sort4_u8_separate() {
    kani::assert(active(), "S3_SORT4_SEPARATE_ACTIVE");
    let src: [u8; 6] = kani::any();
    let before = src;
    let mut dst = [MaybeUninit::<u8>::uninit(); 6];
    dst[0].write(0xa5); dst[5].write(0x5a);
    unsafe { sort4_stable(src.as_ptr().add(1), dst.as_mut_ptr().add(1).cast(), &mut KeyLess::<u8>::new()) };
    // Typed loads retain stock initialization checks, after all actual writes.
    let out = unsafe { [dst[1].assume_init(), dst[2].assume_init(), dst[3].assume_init(), dst[4].assume_init()] };
    kani::assert(post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&before[1..5]), &out), "S3_SORT4_SEPARATE_SORTED_FULL_COUNT");
    kani::assert(src == before, "S3_SORT4_SEPARATE_SOURCE_FRAME");
    kani::assert(unsafe { dst[0].assume_init() == 0xa5 && dst[5].assume_init() == 0x5a }, "S3_SORT4_SEPARATE_CANARIES");
    kani::cover(!ordered(&before[1..5]), "S3_SORT4_SEPARATE_UNSORTED");
    kani::cover(before[1] == before[4], "S3_SORT4_SEPARATE_DUPLICATE");
    kani::cover(out[0] < out[3], "S3_SORT4_SEPARATE_NONCONSTANT");
    kani::cover(true, "S3_SORT4_SEPARATE_USEFUL_RETURN");
}

#[kani::proof_for_contract(sort4_stable)]
#[kani::unwind(50)]
fn s3_sort4_u8_same_alloc() {
    kani::assert(active(), "S3_SORT4_SAME_ACTIVE");
    let before: [u8; 48] = kani::any();
    let mut v = [MaybeUninit::<u8>::uninit(); 48];
    let src: usize = kani::any();
    let dst: usize = kani::any();
    kani::assume(src <= 44 && dst <= 44);
    kani::assume(src + 4 <= dst || dst + 4 <= src);
    for i in 0..48 {
        if i < dst || i >= dst + 4 { v[i].write(before[i]); }
    }
    let p = v.as_mut_ptr().cast::<u8>();
    unsafe { sort4_stable(p.add(src), p.add(dst), &mut KeyLess::<u8>::new()) };
    let out = unsafe { [v[dst].assume_init(), v[dst+1].assume_init(), v[dst+2].assume_init(), v[dst+3].assume_init()] };
    kani::assert(post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&before[src..src + 4]), &out), "S3_SORT4_SAME_SORTED_FULL_COUNT");
    for i in 0..48 {
        kani::assert((dst <= i && i < dst + 4) || unsafe { v[i].assume_init() } == before[i], "S3_SORT4_SAME_OUTSIDE_FRAME");
    }
    for i in 0..4 {
        kani::assert(unsafe { v[src+i].assume_init() } == before[src+i], "S3_SORT4_SAME_SOURCE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 48 && (canary < dst || canary >= dst + 4));
    kani::assert(unsafe { v[canary].assume_init() } == before[canary], "S3_SORT4_SAME_CANARY");
    kani::cover(src + 4 == dst, "S3_SORT4_SAME_FORWARD_ADJACENT");
    kani::cover(dst + 4 == src, "S3_SORT4_SAME_REVERSE_ADJACENT");
    kani::cover(src == 44 && dst == 0, "S3_SORT4_SAME_EXTREME");
    kani::cover(!ordered(&before[src..src + 4]), "S3_SORT4_SAME_UNSORTED");
    kani::cover(before[src] == before[src + 3], "S3_SORT4_SAME_DUPLICATE");
    kani::cover(out[0] < out[3], "S3_SORT4_SAME_NONCONSTANT");
    kani::cover(true, "S3_SORT4_SAME_USEFUL_RETURN");
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(36)]
fn s3_insert_tail_u8_rel16() {
    kani::assert(active(), "S3_INSERT_ACTIVE");
    let mut v: [u8; 34] = kani::any();
    let begin: usize = kani::any();
    let tail: usize = kani::any();
    kani::assume(1 <= begin && begin <= 16 && 1 <= tail && tail <= 16);
    kani::assume(ordered(&v[begin..begin + tail]));
    let before = v;
    let p = unsafe { v.as_mut_ptr().add(begin) };
    unsafe { insert_tail(p, p.add(tail), &mut KeyLess::<u8>::new()) };
    kani::assert(post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&before[begin..begin + tail + 1]), &v[begin..begin + tail + 1]), "S3_INSERT_SORTED_FULL_COUNT");
    for i in 0..34 {
        kani::assert((begin <= i && i <= begin + tail) || v[i] == before[i], "S3_INSERT_OUTSIDE_FRAME");
    }
    kani::cover(tail == 1, "S3_INSERT_LENGTH2");
    kani::cover(tail == 16, "S3_INSERT_LENGTH17");
    kani::cover(begin == 1, "S3_INSERT_BASE_FIRST");
    kani::cover(begin == 16, "S3_INSERT_BASE_LAST");
    kani::cover(before[begin + tail] >= before[begin + tail - 1], "S3_INSERT_EARLY_RETURN");
    kani::cover(before[begin + tail] < before[begin], "S3_INSERT_FULL_SIFT");
    kani::cover(before[begin + tail] == before[begin], "S3_INSERT_DUPLICATE");
    kani::cover(v[begin] < v[begin + tail], "S3_INSERT_NONCONSTANT");
    kani::cover(true, "S3_INSERT_USEFUL_RETURN");
}

#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(12)]
fn s3_merge8_u8_separate() {
    kani::assert(active(), "S3_MERGE8_SEPARATE_ACTIVE");
    let src: [u8; 10] = kani::any();
    kani::assume(ordered(&src[1..5]) && ordered(&src[5..9]));
    let before = src;
    let mut dst = [MaybeUninit::<u8>::uninit(); 10];
    dst[0].write(0xa5); dst[9].write(0x5a);
    unsafe { bidirectional_merge(&src[1..9], dst.as_mut_ptr().add(1).cast(), &mut KeyLess::<u8>::new()) };
    let mut out = [0u8; 8];
    for i in 0..8 { out[i] = unsafe { dst[i + 1].assume_init() }; }
    kani::assert(post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&before[1..9]), &out), "S3_MERGE8_SEPARATE_SORTED_FULL_COUNT");
    kani::assert(src == before, "S3_MERGE8_SEPARATE_SOURCE_FRAME");
    kani::assert(unsafe { dst[0].assume_init() == 0xa5 && dst[9].assume_init() == 0x5a }, "S3_MERGE8_SEPARATE_CANARIES");
    kani::cover(src[1] < src[5], "S3_MERGE8_SEPARATE_LEFT_FIRST");
    kani::cover(src[1] > src[5], "S3_MERGE8_SEPARATE_RIGHT_FIRST");
    kani::cover(src[4] == src[5], "S3_MERGE8_SEPARATE_TIE");
    kani::cover(src[4] > src[5], "S3_MERGE8_SEPARATE_UNSORTED");
    kani::cover(out[0] < out[7], "S3_MERGE8_SEPARATE_NONCONSTANT");
    kani::cover(true, "S3_MERGE8_SEPARATE_USEFUL_RETURN");
}

#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(50)]
fn s3_merge8_u8_same_alloc() {
    kani::assert(active(), "S3_MERGE8_SAME_ACTIVE");
    let before: [u8; 48] = kani::any();
    let mut v = [MaybeUninit::<u8>::uninit(); 48];
    let src: usize = kani::any();
    let dst: usize = kani::any();
    kani::assume(src <= 40 && dst <= 40);
    kani::assume(src + 8 <= dst || dst + 8 <= src);
    kani::assume(ordered(&before[src..src + 4]) && ordered(&before[src + 4..src + 8]));
    for i in 0..48 {
        if i < dst || i >= dst + 8 { v[i].write(before[i]); }
    }
    let p = v.as_mut_ptr().cast::<u8>();
    // Only the source range is borrowed. The disjoint destination retains raw provenance.
    unsafe { bidirectional_merge(slice::from_raw_parts(p.add(src), 8), p.add(dst), &mut KeyLess::<u8>::new()) };
    let mut out = [0u8; 8];
    for i in 0..8 { out[i] = unsafe { v[dst+i].assume_init() }; }
    kani::assert(post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&before[src..src + 8]), &out), "S3_MERGE8_SAME_SORTED_FULL_COUNT");
    for i in 0..48 {
        kani::assert((dst <= i && i < dst + 8) || unsafe { v[i].assume_init() } == before[i], "S3_MERGE8_SAME_OUTSIDE_FRAME");
    }
    for i in 0..8 {
        kani::assert(unsafe { v[src+i].assume_init() } == before[src+i], "S3_MERGE8_SAME_SOURCE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 48 && (canary < dst || canary >= dst + 8));
    kani::assert(unsafe { v[canary].assume_init() } == before[canary], "S3_MERGE8_SAME_CANARY");
    kani::cover(src + 8 == dst, "S3_MERGE8_SAME_FORWARD_ADJACENT");
    kani::cover(dst + 8 == src, "S3_MERGE8_SAME_REVERSE_ADJACENT");
    kani::cover(src == 40 && dst == 0, "S3_MERGE8_SAME_EXTREME");
    kani::cover(before[src] < before[src + 4], "S3_MERGE8_SAME_LEFT_FIRST");
    kani::cover(before[src] > before[src + 4], "S3_MERGE8_SAME_RIGHT_FIRST");
    kani::cover(before[src + 3] == before[src + 4], "S3_MERGE8_SAME_TIE");
    kani::cover(before[src + 3] > before[src + 4], "S3_MERGE8_SAME_UNSORTED");
    kani::cover(out[0] < out[7], "S3_MERGE8_SAME_NONCONSTANT");
    kani::cover(src == 32 && dst == 0, "S3_MERGE8_SAME_SORT8_FIRST_GEOMETRY");
    kani::cover(src == 40 && dst == 16, "S3_MERGE8_SAME_SORT8_SECOND_GEOMETRY");
    kani::cover(true, "S3_MERGE8_SAME_USEFUL_RETURN");
}
