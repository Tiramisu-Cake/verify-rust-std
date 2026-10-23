/*@

pred_ctor r20_u64_array3_content(t: thread_id_t, p: *u64)() =
    array::<u64>(p, 3, ?current) &*& foreach(current, own::<u64>(t));

lem r20_array3_content_to_slice(t: thread_id_t, p: *u64, s: *[u64])
    req r20_u64_array3_content(t, p)() &*&
        strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;
    ens <[u64]>.full_borrow_content(t, s)();
{
    open r20_u64_array3_content(t, p)();
    close slice_full_borrow_content::<u64>(t, s)();
}

lem r20_slice_content_to_array3(t: thread_id_t, p: *u64, s: *[u64])
    req <[u64]>.full_borrow_content(t, s)() &*&
        strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;
    ens r20_u64_array3_content(t, p)();
{
    open slice_full_borrow_content::<u64>(t, s)();
    close r20_u64_array3_content(t, p)();
}

lem r20_array3_borrow_to_slice(k: lifetime_t, t: thread_id_t, p: *u64, s: *[u64])
    req full_borrow(k, r20_u64_array3_content(t, p)) &*&
        strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;
    ens full_borrow(k, <[u64]>.full_borrow_content(t, s));
{
    produce_lem_ptr_chunk implies(r20_u64_array3_content(t, p), <[u64]>.full_borrow_content(t, s))() {
        r20_array3_content_to_slice(t, p, s);
    } {
        produce_lem_ptr_chunk implies(<[u64]>.full_borrow_content(t, s), r20_u64_array3_content(t, p))() {
            r20_slice_content_to_array3(t, p, s);
        } {
            full_borrow_implies(k, r20_u64_array3_content(t, p), <[u64]>.full_borrow_content(t, s));
        }
    }
}

lem r20_slice_borrow_to_array3(k: lifetime_t, t: thread_id_t, p: *u64, s: *[u64])
    req full_borrow(k, <[u64]>.full_borrow_content(t, s)) &*&
        strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;
    ens full_borrow(k, r20_u64_array3_content(t, p));
{
    produce_lem_ptr_chunk implies(<[u64]>.full_borrow_content(t, s), r20_u64_array3_content(t, p))() {
        r20_slice_content_to_array3(t, p, s);
    } {
        produce_lem_ptr_chunk implies(r20_u64_array3_content(t, p), <[u64]>.full_borrow_content(t, s))() {
            r20_array3_content_to_slice(t, p, s);
        } {
            full_borrow_implies(k, <[u64]>.full_borrow_content(t, s), r20_u64_array3_content(t, p));
        }
    }
}

@*/
