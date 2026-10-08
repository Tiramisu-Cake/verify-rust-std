#![no_std]
#![allow(dead_code)]
#![feature(unboxed_closures)]

// Isolated translator matcher controls. Their true contracts deliberately
// provide no call ownership: registration evidence is not a function proof.

// HRTB_BEGIN bool_match
pub unsafe fn bool_match<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
// HRTB_END bool_match

// HRTB_BEGIN nonbool_rhs
pub unsafe fn nonbool_rhs<'cmp, T, F: FnMut(&T, &T) -> u8>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
// HRTB_END nonbool_rhs

// HRTB_BEGIN missing_projection
pub unsafe fn missing_projection<'cmp, T, F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T)>>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
// HRTB_END missing_projection

// HRTB_BEGIN wrong_f
pub unsafe fn wrong_f<'cmp, T, F: FnMut(&T, &T) -> bool, G>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<G, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
// HRTB_END wrong_f

// HRTB_BEGIN wrong_t
pub unsafe fn wrong_t<'cmp, T, U, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp U, &'cmp U), 'cmp>@*/(left, right);
}
// HRTB_END wrong_t

// HRTB_BEGIN unequal_lifetimes
pub unsafe fn unequal_lifetimes<'left, 'right, T, F: FnMut(&T, &T) -> bool>(
    left: &'left T, right: &'right T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'left T, &'right T), 'left>@*/(left, right);
}
// HRTB_END unequal_lifetimes

// HRTB_BEGIN wrong_method_lifetime
pub unsafe fn wrong_method_lifetime<'cmp, 'other, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'other>@*/(left, right);
}
// HRTB_END wrong_method_lifetime

// HRTB_BEGIN nonlifetime_method_arg
pub unsafe fn nonlifetime_method_arg<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), bool>@*/(left, right);
}
// HRTB_END nonlifetime_method_arg

// HRTB_BEGIN shadowed_f
pub unsafe fn shadowed_f<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    /*@ abstract_type F; @*/
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
// HRTB_END shadowed_f

// HRTB_BEGIN shadowed_t
pub unsafe fn shadowed_t<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    /*@ abstract_type T; @*/
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
// HRTB_END shadowed_t

// HRTB_BEGIN duplicate_projection
pub unsafe fn duplicate_projection<'cmp, T,
    F: FnMut(&T, &T) -> bool + for<'a, 'b> FnMut(&'a T, &'b T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
// HRTB_END duplicate_projection

// HRTB_BEGIN no_matching_trait
pub unsafe fn no_matching_trait<'cmp, T, F: FnOnce(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare(left, right);
}
// HRTB_END no_matching_trait

// HRTB_BEGIN second_unannotated
pub unsafe fn second_unannotated<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
    let _ = compare(left, right);
}
// HRTB_END second_unannotated

// HRTB_BEGIN second_body
pub unsafe fn first_body<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}

pub unsafe fn second_body<'cmp, T, F: FnMut(&T, &T) -> u8>(
    left: &'cmp T, right: &'cmp T, compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
// HRTB_END second_body
