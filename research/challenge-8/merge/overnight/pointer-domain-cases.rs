#![allow(dead_code)]
// Checked pure pointer-domain bridge for the actual merge C1 copy call.
// This file introduces no memory resources and carries no guessed rejection
// oracle; intended negative locations are to be calibrated on hosted Actions.

/*@
pred c1_one_pointer_domain<T>(p: *mut T) =
    0 < p as usize &*&
    p as usize % std::mem::align_of::<T>() == 0 &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    p as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    object_pointer_within_limits(p, std::mem::size_of::<T>()) == true;

pred c1_pair_result<T>(src_base: *const T, dst_base: *mut T,
        i: usize, j: usize, src: *const T, dst: *mut T) =
    c1_one_pointer_domain::<T>(src as *mut T) &*&
    c1_one_pointer_domain::<T>(dst) &*&
    (src as pointer) == pointer_ctor(
        (src_base as pointer).provenance,
        (src_base as usize) + i * std::mem::size_of::<T>(),
        (src_base as pointer).metadata) &*&
    (dst as pointer) == pointer_ctor(
        (dst_base as pointer).provenance,
        (dst_base as usize) + j * std::mem::size_of::<T>(),
        (dst_base as pointer).metadata) &*&
    (src as pointer).provenance == (src_base as pointer).provenance &*&
    (src as pointer).metadata == (src_base as pointer).metadata &*&
    (dst as pointer).provenance == (dst_base as pointer).provenance &*&
    (dst as pointer).metadata == (dst_base as pointer).metadata &*&
    ((src as usize) + std::mem::size_of::<T>() <= dst as usize ||
     (dst as usize) + std::mem::size_of::<T>() <= src as usize);

lem address_stride_aligned(base: usize, index: usize, stride: usize, alignment: usize)
    req 0 <= base &*& 0 <= index &*& 0 < stride &*& 0 < alignment &*&
        base % alignment == 0 &*& stride % alignment == 0;
    ens (base + index * stride) % alignment == 0;
{
    div_rem_nonneg(base, alignment);
    div_rem_nonneg(stride, alignment);
    assert base == base / alignment * alignment;
    assert stride == stride / alignment * alignment;
    assert base + index * stride ==
        (base / alignment + index * (stride / alignment)) * alignment;
    div_rem_nonneg_unique(base + index * stride, alignment,
        base / alignment + index * (stride / alignment), 0);
}
@*/

// The checked adapter used to derive C1's pure one-element pointer premises.
// `pointer_within_limits` at each allocation endpoint is an explicit caller
// obligation; this function neither manufactures nor weakens it.
pub unsafe fn c1_pointer_domain_pair<T>(
    src_base: *const T,
    dst_base: *mut T,
    n: usize,
    i: usize,
    j: usize,
) -> (*const T, *mut T)
/*@
req 2 <= n &*& 0 <= i &*& i < n &*& 0 <= j &*& j < n &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    0 < std::mem::align_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 < src_base as usize &*& 0 < dst_base as usize &*&
    src_base as usize % std::mem::align_of::<T>() == 0 &*&
    dst_base as usize % std::mem::align_of::<T>() == 0 &*&
    src_base as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    dst_base as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    pointer_within_limits(src_base) == true &*&
    pointer_within_limits(src_base + n) == true &*&
    pointer_within_limits(dst_base) == true &*&
    pointer_within_limits(dst_base + n) == true &*&
    (src_base as usize + n * std::mem::size_of::<T>() <= dst_base as usize ||
     dst_base as usize + n * std::mem::size_of::<T>() <= src_base as usize);
@*//*@
ens c1_pair_result::<T>(src_base, dst_base, i, j, result.0, result.1);
@*//*@
on_unwind_ens false;
@*/
{
    let s = std::mem::size_of::<T>();
    let a = std::mem::align_of::<T>();
    //@ size_align::<T>();
    let src = unsafe { src_base.add(i) };
    let dst = unsafe { dst_base.add(j) };

    //@ address_stride_aligned(src_base as usize, i, s, a);
    //@ address_stride_aligned(dst_base as usize, j, s, a);
    //@ mul_mono_l(0, i, s);
    //@ mul_mono_l(i + 1, n, s);
    //@ mul_mono_l(0, j, s);
    //@ mul_mono_l(j + 1, n, s);

    // Interior one-element spans lie inside the respective bounded full span.
    // The original provenance bounds at base/base+n therefore cover both the
    // indexed pointer and its one-past endpoint.
    unsafe {
        //@ assert (src as usize) == (src_base as usize) + i * s;
        //@ assert (dst as usize) == (dst_base as usize) + j * s;
        //@ assert object_pointer_within_limits(src, s) == true;
        //@ assert object_pointer_within_limits(dst, s) == true;
        //@ assert (src as usize) + s <= dst as usize || (dst as usize) + s <= src as usize;
        //@ close c1_one_pointer_domain::<T>(src as *mut T);
        //@ close c1_one_pointer_domain::<T>(dst);
        //@ close c1_pair_result::<T>(src_base, dst_base, i, j, src, dst);
    }
    (src, dst)
}

// CASE_BEGIN pointer_domain_pair
pub unsafe fn pointer_domain_pair<T>(
    src_base: *const T,
    dst_base: *mut T,
    n: usize,
    i: usize,
    j: usize,
) -> (*const T, *mut T)
/*@
req 2 <= n &*& 0 <= i &*& i < n &*& 0 <= j &*& j < n &*&
    0 < std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= isize::MAX &*&
    0 < std::mem::align_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 < src_base as usize &*& 0 < dst_base as usize &*&
    src_base as usize % std::mem::align_of::<T>() == 0 &*&
    dst_base as usize % std::mem::align_of::<T>() == 0 &*&
    src_base as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    dst_base as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    pointer_within_limits(src_base) == true &*&
        pointer_within_limits(src_base + n) == true &*&
    pointer_within_limits(dst_base) == true &*&
        pointer_within_limits(dst_base + n) == true &*&
    (src_base as usize + n * std::mem::size_of::<T>() <= dst_base as usize ||
     dst_base as usize + n * std::mem::size_of::<T>() <= src_base as usize);
@*//*@
ens c1_pair_result::<T>(src_base, dst_base, i, j, result.0, result.1);
@*//*@
on_unwind_ens false;
@*/
{
    unsafe { c1_pointer_domain_pair(src_base, dst_base, n, i, j) }
}
// CASE_END pointer_domain_pair

// CASE_BEGIN pointer_domain_out_of_index
pub unsafe fn pointer_domain_out_of_index<T>(
    src_base: *const T,
    dst_base: *mut T,
    n: usize,
    j: usize,
) -> ()
/*@
req 2 <= n &*& 0 <= j &*& j < n &*&
    0 < std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= isize::MAX &*&
    0 < std::mem::align_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 < src_base as usize &*& 0 < dst_base as usize &*&
    src_base as usize % std::mem::align_of::<T>() == 0 &*&
    dst_base as usize % std::mem::align_of::<T>() == 0 &*&
    src_base as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    dst_base as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    pointer_within_limits(src_base) == true &*&
    pointer_within_limits(src_base + n) == true &*&
    pointer_within_limits(dst_base) == true &*&
    pointer_within_limits(dst_base + n) == true &*&
    (src_base as usize + n * std::mem::size_of::<T>() <= dst_base as usize ||
     dst_base as usize + n * std::mem::size_of::<T>() <= src_base as usize);
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let _pair = unsafe { c1_pointer_domain_pair(src_base, dst_base, n, n, j) }; // TARGET: i == n violates the checked index precondition
}
// CASE_END pointer_domain_out_of_index

// CASE_BEGIN pointer_domain_overlap
pub unsafe fn pointer_domain_overlap<T>(base: *mut T, n: usize, i: usize, j: usize) -> ()
/*@
req 2 <= n &*& 0 <= i &*& i < n &*& 0 <= j &*& j < n &*&
    0 < std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= isize::MAX &*&
    0 < std::mem::align_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 < base as usize &*&
    base as usize % std::mem::align_of::<T>() == 0 &*&
    base as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    pointer_within_limits(base) == true &*&
    pointer_within_limits(base + n) == true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let _pair = unsafe { c1_pointer_domain_pair(base as *const T, base, n, i, j) }; // TARGET: identical full ranges violate the checked separation precondition
}
// CASE_END pointer_domain_overlap
