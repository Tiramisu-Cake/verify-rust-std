#!/usr/bin/env python3
"""Isolated generated-glue evidence gate tests; no proof tools or evidence access."""
import importlib.util
from pathlib import Path
import sys

TARGET = Path(__file__).with_name("onecell-selected-drop.py")
spec = importlib.util.spec_from_file_location("selected_drop_service_test", TARGET)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

call_loc = "verified/lib.rs(10,5-19)"
copy_loc = "verified/lib.rs(9,5-13)"
ast = {"glue_selected_method_call_loc": call_loc,
       "glue_receiver_copy_loc": copy_loc}
success = (
    "verified/lib.rs(4,1-10): Verifying function 'core::__vf_generated_drop_glue'\n"
    f"  0.101s: {copy_loc}: Executing statement\n"
    f"  0.153s: {call_loc}: Executing statement\n"
    f"  0.153s: {call_loc}: Verifying function call\n"
    "verified/lib.rs(12,1-5): Executing return statement\n"
    "verified/lib.rs(12,1-5): Leak check.\n"
    "verified/lib.rs(20,1-5): Verifying function 'natural_onecell'\n")
assert module._generated_glue_proof_gate(success, ast)["admitted"]

cases = (
    # No marker elsewhere in a caller or selected-method segment can stand in.
    success.replace(f"  0.153s: {call_loc}: Executing statement\n", ""),
    success.replace(f"  0.153s: {call_loc}: Verifying function call\n", ""),
    success.replace(f"{copy_loc}: Executing statement\n", ""),
    success.replace(call_loc, "verified/lib.rs(10,6-20)"),
    success.replace("Executing return statement", "Returning"),
    success.replace("Leak check.", ""),
    success.replace("Leak check.\n", "Leak check.\n"
                     "verified/lib.rs(11,1-5): error: failure\n"),
    success.replace("Leak check.\n", "Leak check.\n"
                     "verified/lib.rs(11,1-5): dead code\n"),
    success.replace("core::__vf_generated_drop_glue", "fake__vf_generated_drop_glue"),
    success + "Verifying function '__vf_generated_drop_glue'\n",
    (success.replace(f"  0.101s: {copy_loc}: Executing statement\n", "")
     .replace(f"  0.153s: {call_loc}: Executing statement\n", "")
     .replace(f"  0.153s: {call_loc}: Verifying function call\n", "")
     .replace("verified/lib.rs(12,1-5): Executing return statement\n", "")
     .replace("verified/lib.rs(12,1-5): Leak check.\n", "")
     .replace("verified/lib.rs(20,1-5): Verifying function 'natural_onecell'\n",
              "verified/lib.rs(20,1-5): Verifying function 'natural_onecell'\n"
              f"  0.200s: {call_loc}: Executing statement\n"
              f"  0.200s: {call_loc}: Verifying function call\n"
              "  0.201s: Executing return statement\n"
              "  0.201s: Leak check.\n")),
)
for log in cases:
    assert not module._generated_glue_proof_gate(log, ast)["admitted"], log

assert module._is_generated_glue_name("__vf_generated_drop_glue")
assert module._is_generated_glue_name("core::__vf_generated_drop_glue")
assert not module._is_generated_glue_name("fake__vf_generated_drop_glue")
print("PASS_SERVICE_ONLY: generated glue requires unique local runtime proof evidence")
