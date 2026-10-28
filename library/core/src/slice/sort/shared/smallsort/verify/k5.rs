//! K5 C: specialized trait form and independent contract/no-contract controls.
use super::super::UnstableSmallSortTypeImpl;
use crate::cell::Cell;
use crate::kani;

#[kani::proof_for_contract(<u64 as UnstableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(6)]
fn specialized_u64() {
    let mut v: [u64; 4] = kani::any();
    let n: usize = kani::any();
    kani::assume(n <= 4);
    kani::cover(n >= 2, "K5 specialized u64 call N>=2");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v[..n], &mut |a, b| a < b);
    kani::cover(n >= 2, "K5 specialized u64 return N>=2");
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl::small_sort)]
#[kani::unwind(6)]
fn trait_path_u64() {
    let mut v: [u64; 4] = kani::any();
    let n: usize = kani::any();
    kani::assume(n <= 4);
    kani::cover(n >= 2, "K5 trait-path u64 call N>=2");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v[..n], &mut |a, b| a < b);
    kani::cover(n >= 2, "K5 trait-path u64 return N>=2");
}

#[kani::ensures(|_| true)]
#[kani::modifies(v)]
fn free_wrapper(v: &mut [Cell<u8>]) {
    <Cell<u8> as UnstableSmallSortTypeImpl>::small_sort(v, &mut |a, b| a.get() < b.get());
}

#[kani::proof_for_contract(free_wrapper)]
#[kani::unwind(6)]
fn free_wrapper_cell() {
    let mut v = [Cell::new(kani::any::<u8>()), Cell::new(kani::any::<u8>())];
    let n: usize = kani::any();
    kani::assume(n <= 2);
    kani::cover(n >= 2, "K5 free Cell wrapper call N>=2");
    free_wrapper(&mut v[..n]);
    kani::cover(n >= 2, "K5 free Cell wrapper return N>=2");
}

// This trait is the reduced B example with ONLY the default contract removed.
trait SmallSort { fn small_sort(v: &mut [u8]); }
impl<T> SmallSort for T {
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
#[kani::proof_for_contract(control)]
#[kani::unwind(3)]
fn reduced_free_form() {
    let mut plain_default: [u8; 2] = kani::any();
    let before = plain_default;
    kani::cover(true, "K5 reduced uncontracted default call N=2");
    <u16 as SmallSort>::small_sort(&mut plain_default);
    assert!(plain_default[0] <= plain_default[1]);
    assert!(plain_default == before || plain_default == [before[1], before[0]]);
    kani::cover(true, "K5 reduced uncontracted default return N=2");
    <u8 as SmallSort>::small_sort(&mut plain_default);
    kani::cover(true, "K5 reduced uncontracted specialized return N=2");
    let mut v: [u8; 2] = kani::any();
    kani::cover(true, "free control call N=2");
    control(&mut v);
    kani::cover(true, "free control return N=2");
}

#[kani::ensures(|_| false)]
#[kani::modifies(v)]
fn false_control(v: &mut [u8]) { pair(v); }
#[kani::proof_for_contract(false_control)]
#[kani::unwind(3)]
fn reject_false() {
    let mut v: [u8; 2] = kani::any();
    kani::cover(true, "K5 false contract call N=2");
    false_control(&mut v);
    kani::cover(true, "K5 false contract return N=2");
}
