#![no_std]
#![allow(dead_code)]
#![feature(unboxed_closures)]

// Translator-only regression cases. These deliberately have req/ens true and
// provide no ownership for a successful call proof.

#[cfg(hrtb_positive)]
pub unsafe fn positive<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T,
    right: &'cmp T,
    less: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}

#[cfg(hrtb_u8)]
pub unsafe fn non_boolean<'cmp, T, F: FnMut(&T, &T) -> u8>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}

#[cfg(hrtb_no_output)]
pub unsafe fn unconstrained_output<'cmp, T, F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T)>>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}

#[cfg(hrtb_wrong_f)]
pub unsafe fn wrong_function_type<'cmp, T, F: FnMut(&T, &T) -> bool, G>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<G, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}

#[cfg(hrtb_wrong_t)]
pub unsafe fn wrong_referent_type<'cmp, T, U, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp U, &'cmp U), 'cmp>@*/(left, right);
}

#[cfg(hrtb_unequal_lifetimes)]
pub unsafe fn unequal_lifetimes<'left, 'right, T, F: FnMut(&T, &T) -> bool>(
    left: &'left T,
    right: &'right T,
    compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'left T, &'right T), 'left>@*/(left, right);
}

#[cfg(hrtb_second_call)]
pub unsafe fn second_call_unannotated<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
    let _ = compare(left, right);
}

#[cfg(hrtb_second_body)]
pub unsafe fn first_body<'cmp, T, F: FnMut(&T, &T) -> bool>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}

#[cfg(hrtb_second_body)]
pub unsafe fn second_body<'cmp, T, F: FnMut(&T, &T) -> u8>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) /*@ req true; @*/ /*@ ens true; @*/ {
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
}
