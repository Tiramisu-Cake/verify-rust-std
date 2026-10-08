#![no_std]
#![allow(dead_code)]

/*@
pred live<T>() = true;
@*/

pub unsafe fn lifetime_test_positive<T>()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ let probe = 0;
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ close live::<T>();
        //@ end_lft_binding::<'cmp>();
        //@ open live::<T>();
        //@ assert lifetime_token(cmp_k);
        //@ end_lifetime(cmp_k);
    }
}
