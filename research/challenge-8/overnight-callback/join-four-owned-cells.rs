/*@
lem join_four_owned_cells<T>(base: *T, t: thread_id_t)
    req *base |-> ?first &*& <T>.own(t, first) &*&
        *(base + 1) |-> ?second &*& <T>.own(t, second) &*&
        *(base + 2) |-> ?third &*& <T>.own(t, third) &*&
        *(base + 3) |-> ?fourth &*& <T>.own(t, fourth);
    ens base[..4] |-> cons(first, cons(second, cons(third, cons(fourth, nil)))) &*&
        foreach(cons(first, cons(second, cons(third, cons(fourth, nil)))),
            own::<T>(t));
{
    points_to_limits(base);
    points_to_limits(base + 1);
    points_to_limits(base + 2);
    points_to_limits(base + 3);
    note(pointer_within_limits(base));
    note(pointer_within_limits(base + 1));
    note(pointer_within_limits(base + 2));
    note(pointer_within_limits(base + 3));
    note(pointer_within_limits(base + 4));
    close own::<T>(t)(first);
    close own::<T>(t)(second);
    close own::<T>(t)(third);
    close own::<T>(t)(fourth);
    close foreach(nil, own::<T>(t));
    close foreach(cons(fourth, nil), own::<T>(t));
    close foreach(cons(third, cons(fourth, nil)), own::<T>(t));
    close foreach(cons(second, cons(third, cons(fourth, nil))), own::<T>(t));
    close foreach(cons(first, cons(second, cons(third, cons(fourth, nil)))),
        own::<T>(t));
    close array(base + 4, 0, nil);
    close array(base + 3, 1, cons(fourth, nil));
    close array(base + 2, 2, cons(third, cons(fourth, nil)));
    close array(base + 1, 3, cons(second, cons(third, cons(fourth, nil))));
    close array(base, 4, cons(first, cons(second, cons(third, cons(fourth, nil)))));
}
@*/
