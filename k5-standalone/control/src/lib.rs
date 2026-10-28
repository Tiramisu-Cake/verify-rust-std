#![feature(min_specialization)]
#[cfg(kani)]
mod check {
    trait SmallSort { fn small_sort(v: &mut [u8]); }
    impl<T> SmallSort for T {
        default fn small_sort(v: &mut [u8]) { pair(v); }
    }
    impl SmallSort for u8 {
        #[kani::ensures(|_| true)]
        #[kani::modifies(v)]
        fn small_sort(v: &mut [u8]) { pair(v); }
    }
    fn pair(v: &mut [u8]) {
        if v.len() == 2 && v[1] < v[0] { v.swap(0, 1); }
    }
    #[kani::proof_for_contract(<u8 as SmallSort>::small_sort)]
    #[kani::unwind(3)]
    fn check_control() {
        let mut v: [u8; 2] = kani::any();
        kani::cover(true, "control call N=2");
        <u8 as SmallSort>::small_sort(&mut v);
        kani::cover(true, "control return N=2");
    }
}
