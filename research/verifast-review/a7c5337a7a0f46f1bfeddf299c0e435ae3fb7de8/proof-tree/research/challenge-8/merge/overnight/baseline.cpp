// SPDX-License-Identifier: Apache-2.0 OR MIT
// Stock C++ verifier arithmetic control; independent of the Rust frontend.
int overnight_cpp_arithmetic_identity(int x)
    //@ requires true;
    //@ ensures result == 0;
{
    int y = x - x;
    //@ assert y == 0;
    return y;
}
