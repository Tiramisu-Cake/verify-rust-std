// CASE prefix-native
// The native entry contract is deliberately untouched in this case.
return;
// END CASE

// CASE source-frame-positive
/*@
if (true) {
    assert thread_token(?t);
    assert t == currentThread;
    assert v_base[..len] |-> ?source_all;
    assert foreach(source_all, own::<T>(t));
    assert *is_less |-> ?less_before;
    assert <F>.own(t, less_before);
    array_split::<T>(v_base, 4);
    foreach_split(source_all, own::<T>(t), 4);
    assert v_base[..4] |-> ?first_four;
    assert foreach(first_four, own::<T>(t));
    assert *is_less |-> less_before;
    assert <F>.own(t, less_before);
    array_join::<T>(v_base);
    foreach_append(take(4, source_all), drop(4, source_all));
    assert v_base[..len] |-> source_all;
    assert foreach(source_all, own::<T>(t));
}
@*/
return;
// END CASE

// CASE bridge-positive
/*@
if (0 < std::mem::size_of::<T>()) {
    assert thread_token(?t);
    assert t == currentThread;
    assert v_base[..len] |-> ?source_all;
    assert foreach(source_all, own::<T>(t));
    assert *is_less |-> ?less_before;
    assert <F>.own(t, less_before);

    array_split::<T>(v_base, 4);
    foreach_split(source_all, own::<T>(t), 4);

    let scratch_len = ptr_len(scratch);
    let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
    assert mu_base[..scratch_len] |-> ?mu_all;
    assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
    array_split::<std::mem::MaybeUninit<T>>(mu_base, 4);

    open array::<std::mem::MaybeUninit<T>>(mu_base, 4, ?mu_first4);
    assert *mu_base |-> ?mu0;
    std::mem::open_MaybeUninit::<T>(mu_base);
    open array::<std::mem::MaybeUninit<T>>(mu_base + 1, 3, ?mu_rest3);
    assert *(mu_base + 1) |-> ?mu1;
    std::mem::open_MaybeUninit::<T>(mu_base + 1);
    open array::<std::mem::MaybeUninit<T>>(mu_base + 2, 2, ?mu_rest2);
    assert *(mu_base + 2) |-> ?mu2;
    std::mem::open_MaybeUninit::<T>(mu_base + 2);
    open array::<std::mem::MaybeUninit<T>>(mu_base + 3, 1, ?mu_rest1);
    assert *(mu_base + 3) |-> ?mu3;
    std::mem::open_MaybeUninit::<T>(mu_base + 3);
    open array::<std::mem::MaybeUninit<T>>(mu_base + 4, 0, nil);

    assert *scratch_base |-?-> ?storage0;
    points_to__limits::<T>(scratch_base + 0);
    assert *(scratch_base + 1) |-?-> ?storage1;
    points_to__limits::<T>(scratch_base + 1);
    assert *(scratch_base + 2) |-?-> ?storage2;
    points_to__limits::<T>(scratch_base + 2);
    assert *(scratch_base + 3) |-?-> ?storage3;
    points_to__limits::<T>(scratch_base + 3);
    close array_::<T>(scratch_base + 4, 0, nil);
    close array_::<T>(scratch_base + 3, 1, cons(storage3, nil));
    close array_::<T>(scratch_base + 2, 2, cons(storage2, cons(storage3, nil)));
    close array_::<T>(scratch_base + 1, 3, cons(storage1, cons(storage2, cons(storage3, nil))));
    close array_::<T>(scratch_base, 4,
        cons(storage0, cons(storage1, cons(storage2, cons(storage3, nil)))));
    assert pointer_within_limits(scratch_base);
    assert pointer_within_limits(scratch_base + 4);

    assert array_::<T>(scratch_base, 4, ?destination_before);
    assert type_interp::<T>();
    assert type_interp::<F>();
    c1_entry_identity::<T, F>(v_base, scratch_base, is_less as *mut F);

    open array_::<T>(scratch_base, 4, destination_before);
    open array_::<T>(scratch_base + 1, 3, ?options3);
    open array_::<T>(scratch_base + 2, 2, ?options2);
    open array_::<T>(scratch_base + 3, 1, ?option3);
    open array_::<T>(scratch_base + 4, 0, nil);
    std::mem::close_MaybeUninit_::<T>(mu_base + 3);
    assert *(mu_base + 3) |-> mu3;
    std::mem::close_MaybeUninit_::<T>(mu_base + 2);
    assert *(mu_base + 2) |-> mu2;
    std::mem::close_MaybeUninit_::<T>(mu_base + 1);
    assert *(mu_base + 1) |-> mu1;
    std::mem::close_MaybeUninit_::<T>(mu_base);
    assert *mu_base |-> mu0;

    close array::<std::mem::MaybeUninit<T>>(mu_base + 4, 0, nil);
    close array::<std::mem::MaybeUninit<T>>(mu_base + 3, 1, cons(mu3, nil));
    close array::<std::mem::MaybeUninit<T>>(mu_base + 2, 2, cons(mu2, cons(mu3, nil)));
    close array::<std::mem::MaybeUninit<T>>(mu_base + 1, 3, cons(mu1, cons(mu2, cons(mu3, nil))));
    close array::<std::mem::MaybeUninit<T>>(mu_base, 4, cons(mu0, cons(mu1, cons(mu2, cons(mu3, nil)))));
    array_join::<std::mem::MaybeUninit<T>>(mu_base);
    array_join::<T>(v_base);
    foreach_append(take(4, source_all), drop(4, source_all));
    assert mu_base[..scratch_len] |-> mu_all;
    assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
    assert v_base[..len] |-> source_all;
    assert foreach(source_all, own::<T>(t));
}
@*/
return;
// END CASE

// CASE range-negative
//@ array_split::<T>(v_base, len + 1); // RANGE_AUTHORITY_CONTROL
return;
// END CASE

// CASE duplicate-negative
//@ assert v_base[..len] |-> ?xs &*& v_base[..len] |-> xs; // DUPLICATE_AUTHORITY_CONTROL
return;
// END CASE
