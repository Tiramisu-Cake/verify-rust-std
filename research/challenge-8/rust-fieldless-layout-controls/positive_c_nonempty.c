// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
struct CNonempty {
    unsigned char byte;
};

int c_nonempty_layout_control(void)
/*@ requires true; @*/
/*@
ensures sizeof(struct CNonempty) >= 1;
@*/
{
    //@ assert sizeof(struct CNonempty) >= 1;
    return 0;
}
