"""Small source/refinement/verifier gates for the experimental Rust ZST model."""

GATES = {
    "generic-guard-no-scratch": {
        "target": "small_sort_general_with_scratch", "positive": True,
        "source": '''#![allow(dead_code, unused_variables)]
fn small_sort_general_with_scratch<T>(v: &mut [T]) {
    let n = v.len();
    if std::mem::size_of::<T>() == 0 { return; }
    if n >= 8 { //@ assert n >= 8;
    }
}
'''
    },
    "generic-guard-unused-mu-scratch": {
        "target": "small_sort_general_with_scratch", "positive": True,
        "source": '''#![allow(dead_code, unused_variables)]
use std::mem::MaybeUninit;
fn small_sort_general_with_scratch<T>(v: &mut [T], scratch: &mut [MaybeUninit<T>]) {
    let n = v.len();
    if std::mem::size_of::<T>() == 0 { return; }
    if n >= 8 { //@ assert n >= 8;
    }
}
'''
    },
    "generic-pre-guard-positive-assert-no-scratch": {
        "target": "small_sort_general_with_scratch", "positive": False,
        "assertion": "std::mem::size_of::<T>() > 0",
        "source": '''#![allow(dead_code, unused_variables)]
fn small_sort_general_with_scratch<T>(v: &mut [T]) {
    //@ assert std::mem::size_of::<T>() > 0;
    let n = v.len();
    if std::mem::size_of::<T>() == 0 { return; }
    if n >= 8 { //@ assert n >= 8;
    }
}
'''
    },
    "generic-pre-guard-positive-assert-mu-scratch": {
        "target": "small_sort_general_with_scratch", "positive": False,
        "assertion": "std::mem::size_of::<T>() > 0",
        "source": '''#![allow(dead_code, unused_variables)]
use std::mem::MaybeUninit;
fn small_sort_general_with_scratch<T>(v: &mut [T], scratch: &mut [MaybeUninit<T>]) {
    //@ assert std::mem::size_of::<T>() > 0;
    let n = v.len();
    if std::mem::size_of::<T>() == 0 { return; }
    if n >= 8 { //@ assert n >= 8;
    }
}
'''
    },
    "generic-post-nonzero-assert": {
        "target": "small_sort_general_with_scratch", "positive": True,
        "source": '''#![allow(dead_code, unused_variables)]
fn small_sort_general_with_scratch<T>(v: &mut [T]) {
    let n = v.len();
    if std::mem::size_of::<T>() == 0 { return; }
    //@ assert std::mem::size_of::<T>() > 0;
    if n >= 8 { //@ assert n >= 8;
    }
}
'''
    },
    "generic-post-nonzero-assert-mu-scratch": {
        "target": "small_sort_general_with_scratch", "positive": True,
        "source": '''#![allow(dead_code, unused_variables)]
use std::mem::MaybeUninit;
fn small_sort_general_with_scratch<T>(v: &mut [T], scratch: &mut [MaybeUninit<T>]) {
    let n = v.len();
    if std::mem::size_of::<T>() == 0 { return; }
    //@ assert std::mem::size_of::<T>() > 0;
    if n >= 8 { //@ assert n >= 8;
    }
}
'''
    },
    "layout-zst-and-nonzst-matrix": {
        "target": "main", "positive": True,
        "source": '''#![allow(dead_code, unused_variables)]
struct Empty;
#[repr(C)] struct EmptyC;
fn main() {
    //@ assert std::mem::size_of::<()>() == 0;
    //@ assert std::mem::size_of::<std::mem::MaybeUninit<()>>() == 0;
    //@ assert std::mem::size_of::<Empty>() == 0;
    //@ assert std::mem::size_of::<EmptyC>() == 0;
    //@ assert std::mem::size_of::<u8>() > 0;
    //@ assert std::mem::size_of::<std::mem::MaybeUninit<u8>>() > 0;
    //@ assert std::mem::size_of::<[(); 0]>() == 0;
    //@ assert std::mem::size_of::<[(); 3]>() == 0;
    //@ assert std::mem::size_of::<[u8; 0]>() == 0;
    //@ std::alloc::is_valid_layout_size_of_align_of::<()>();
    //@ std::alloc::is_valid_layout_size_of_align_of::<EmptyC>();
    //@ std::alloc::is_valid_layout_size_of_align_of::<u8>();
    //@ size_align::<()>();
    //@ size_align::<EmptyC>();
    //@ size_align::<u8>();
    //@ assert std::mem::align_of::<()>() > 0;
    //@ assert std::mem::align_of::<EmptyC>() > 0;
    //@ assert std::mem::align_of::<u8>() > 0;
    //@ assert std::mem::size_of::<()>() % std::mem::align_of::<()>() == 0;
    //@ assert std::mem::size_of::<EmptyC>() % std::mem::align_of::<EmptyC>() == 0;
    //@ assert std::mem::size_of::<u8>() % std::mem::align_of::<u8>() == 0;
}
'''
    },
    "reachable-concrete-zst-false": {
        "target": "small_sort_general_with_scratch", "positive": False,
        "assertion": "false",
        "source": '''#![allow(dead_code, unused_variables)]
use std::mem::MaybeUninit;
fn small_sort_general_with_scratch(v: &mut [()], scratch: &mut [MaybeUninit<()>]) {
    //@ assert false;
}
'''
    },
    "zst-no-extra-permission": {
        "target": "no_permission", "positive": False,
        "assertion": "*p |-> ?value", "expected_error": "No matching heap chunks",
        "source": '''#![allow(dead_code, unused_variables)]
use std::mem::MaybeUninit;
fn no_permission(v: &mut [()], scratch: &mut [MaybeUninit<()>], p: *mut ()) {
    //@ assert *p |-> ?value;
}
'''
    },
}

C_CONTROLS = {
    "c-nonempty": '''struct CNonempty { unsigned char byte; };
int c_nonempty_layout_control(void)
/*@ requires true; @*/
/*@ ensures sizeof(struct CNonempty) >= 1; @*/
{
    //@ assert sizeof(struct CNonempty) >= 1;
    return 0;
}
''',
    "cpp-empty": '''struct CppEmpty {};
int cpp_empty_layout_control()
/*@ requires true; @*/
/*@ ensures sizeof(struct CppEmpty) >= 1; @*/
{
    //@ assert sizeof(struct CppEmpty) >= 1;
    return 0;
}
''',
}
