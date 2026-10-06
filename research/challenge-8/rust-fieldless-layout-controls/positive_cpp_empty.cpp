// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
struct CppEmpty {};

int cpp_empty_layout_control()
/*@ requires true; @*/
/*@
ensures sizeof(struct CppEmpty) >= 1;
@*/
{
    //@ assert sizeof(struct CppEmpty) >= 1;
    return 0;
}
