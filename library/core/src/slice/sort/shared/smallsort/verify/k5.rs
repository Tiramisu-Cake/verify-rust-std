//! K5 stage A: contract form only; Cell selects !Freeze, u64 selects Freeze/Copy.
use super::super::UnstableSmallSortTypeImpl;
use crate::cell::Cell;
use crate::kani;

#[kani::proof_for_contract(<u64 as UnstableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(6)]
fn form_u64() {
    let mut v: [u64; 4] = kani::any();
    let n: usize = kani::any();
    kani::assume(n <= 4);
    kani::cover(n >= 2, "K5 u64 call N>=2");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v[..n], &mut |a, b| a < b);
    kani::cover(n >= 2, "K5 u64 return N>=2");
}

#[kani::proof_for_contract(<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(6)]
fn form_cell() {
    let mut v = [Cell::new(kani::any::<u8>()), Cell::new(kani::any::<u8>())];
    kani::cover(true, "K5 Cell call N=2");
    <Cell<u8> as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut |a, b| a.get() < b.get());
    kani::cover(true, "K5 Cell return N=2");
}
