#![feature(min_specialization)]
// GCB embeds this exact file in core; standalone Kani does not set the controls cfg.
#[cfg(kani_smallsort_controls)]
use crate::kani;
#[cfg(not(kani_smallsort_controls))]
extern crate kani;
trait SmallSort { fn small_sort(v: &mut [u8]); }
impl<T> SmallSort for T {
    #[kani::ensures(|_| true)]
    #[kani::modifies(v)]
    default fn small_sort(v: &mut [u8]) { pair(v); }
}
impl SmallSort for u8 {
    fn small_sort(v: &mut [u8]) { pair(v); }
}
fn pair(v: &mut [u8]) {
    if v.len() == 2 && v[1] < v[0] { v.swap(0, 1); }
}
#[kani::ensures(|_| true)]
#[kani::modifies(v)]
fn control(v: &mut [u8]) { pair(v); }
#[kani::proof_for_contract(<u16 as SmallSort>::small_sort)]
#[kani::unwind(3)]
fn default_form() {
    let mut v: [u8; 2] = kani::any();
    kani::cover(true, "reduced default call N=2");
    <u16 as SmallSort>::small_sort(&mut v);
    kani::cover(true, "reduced default return N=2");
}
#[kani::proof_for_contract(control)]
#[kani::unwind(3)]
fn free_form() {
    let mut v: [u8; 2] = kani::any();
    kani::cover(true, "free control call N=2");
    control(&mut v);
    kani::cover(true, "free control return N=2");
}
fn main() {}
