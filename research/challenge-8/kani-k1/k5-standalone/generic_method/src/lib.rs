#![feature(min_specialization)]
#[cfg(kani)]
mod check {
    trait SmallSort { fn small_sort<F: FnMut(&u8, &u8) -> bool>(v: &mut [u8], less: &mut F); }
    impl<T> SmallSort for T {
        default fn small_sort<F: FnMut(&u8, &u8) -> bool>(v: &mut [u8], _less: &mut F) { pair(v); }
    }
    impl SmallSort for u8 {
        #[kani::ensures(|_| true)]
        #[kani::modifies(v)]
        fn small_sort<F: FnMut(&u8, &u8) -> bool>(v: &mut [u8], _less: &mut F) { pair(v); }
    }
    fn pair(v: &mut [u8]) { if v.len() == 2 && v[1] < v[0] { v.swap(0, 1); } }
    #[kani::proof_for_contract(<u8 as SmallSort>::small_sort)]
    #[kani::unwind(3)]
    fn check_generic() {
        let mut v: [u8; 2] = kani::any();
        let mut less = |a: &u8, b: &u8| a < b;
        kani::cover(true, "generic method call N=2");
        <u8 as SmallSort>::small_sort(&mut v, &mut less);
        kani::cover(true, "generic method return N=2");
    }
}
