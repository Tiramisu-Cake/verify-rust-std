#!/usr/bin/env python3
"""Cloud-only source certificate and disposable generic constructor MIR unit."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PINS = HERE / "SOURCE-PINS.json"
FILE_SHA = {
    "library/core/src/mem/maybe_uninit.rs":
        "1230d267542337ee2842c29d8227cf8a58fe75c53a2a70efaee3922c4e8e25c0",
    "library/core/src/mem/manually_drop.rs":
        "f9cce798828cc852c00feeea9a6218c225b68d92727a5edbddc7c08a731a4f25",
    "library/core/src/hint.rs":
        "ce89716d46b8060db2c2da1aef1d4bcccf90e0804fc021d4470c55203501315f",
}
UNION_PREFIX = (
    b'#[stable(feature = "maybe_uninit", since = "1.36.0")]\n'
    b'// Lang item so we can wrap other types in it. This is useful for coroutines.\n'
    b'#[lang = "maybe_uninit"]\n'
    b'#[derive(Copy)]\n'
    b'#[repr(transparent)]\n'
    b'#[rustc_pub_transparent]\n'
)
NEW_ATTRS = (
    b'    #[stable(feature = "maybe_uninit", since = "1.36.0")]\n'
    b'    #[rustc_const_stable(feature = "const_maybe_uninit", since = "1.36.0")]\n'
    b'    #[must_use = "use `forget` to avoid running Drop code"]\n'
    b'    #[inline(always)]\n'
)
SELECT_BEGIN = b"pub const fn select_unpredictable<T>"
SELECT_END = b"/// The expected temporal locality of a memory prefetch operation."


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def provider(cloud_dir: Path) -> dict:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         not os.environ.get("GITHUB_ACTIONS"), "identified Cloud Build required")
    path = cloud_dir / "provider.py"
    spec = importlib.util.spec_from_file_location("generic_new_cloud_provider", path)
    need(spec is not None and spec.loader is not None, "Cloud provider module absent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    identity = module.require_supported_provider()
    need(identity["provider"] == "cloud-build", "unsupported Cloud provider")
    return identity


def brace_item(data: bytes, signature: bytes) -> bytes:
    need(data.count(signature) == 1, "source item signature not unique")
    start = data.index(signature) + len(signature)
    brace = data.find(b"{", start)
    need(brace >= 0, "source item body absent")
    # The two pinned items are tiny and their exact expected body bytes are
    # checked below; no general Rust syntax extractor is being asserted.
    depth = 0
    for at in range(brace, len(data)):
        if data[at:at + 1] == b"{":
            depth += 1
        elif data[at:at + 1] == b"}":
            depth -= 1
            if depth == 0:
                return data[brace:at + 1]
    raise RuntimeError("source item body is unbalanced")


def prepare(a) -> dict:
    provider_identity = provider(a.cloud_dir)
    need(str(a.proof_root).startswith("/workspace/") and
         str(a.evidence).startswith("/workspace/") and
         not a.evidence.exists(), "fresh /workspace proof/evidence required")
    pins = json.loads(PINS.read_text())
    need(pins.get("classification") == "GENERIC_NEW_SOURCE_ONLY_PIN_NOT_PROOF" and
         pins.get("files_sha256") == FILE_SHA and
         pins.get("different_defid_from_actual_core") is True and
         pins.get("accepted") is False, "source pin manifest differs")
    files = {rel: (a.proof_root / rel).read_bytes() for rel in FILE_SHA}
    need(all(sha(files[rel]) == digest for rel, digest in FILE_SHA.items()),
         "pinned complete std source changed")
    std = files["library/core/src/mem/maybe_uninit.rs"]
    hint = files["library/core/src/hint.rs"]
    union_sig = pins["union_signature"].encode()
    impl_sig = pins["inherent_impl_signature"].encode()
    new_sig = pins["new_signature"].encode()
    union_fields = pins["union_fields"].encode()
    new_body = pins["new_body"].encode()
    need(brace_item(std, union_sig) == union_fields and
         brace_item(std, new_sig) == new_body and
         std.count(impl_sig + b" {") == 1 and
         std.index(impl_sig + b" {") < std.index(new_sig),
         "generic union fields or constructor body/signature changed")
    union_at = std.index(union_sig)
    new_at = std.index(new_sig)
    need(std[union_at - len(UNION_PREFIX):union_at] == UNION_PREFIX and
         std[new_at - 4 - len(NEW_ATTRS):new_at - 4] == NEW_ATTRS and
         std[new_at - 4:new_at] == b"    ",
         "generic union/constructor metadata changed")
    need(hint.count(SELECT_BEGIN) == hint.count(SELECT_END) == 1 and
         hint.index(SELECT_BEGIN) < hint.index(SELECT_END),
         "actual select source bounds changed")
    actual_select = hint[hint.index(SELECT_BEGIN):hint.index(SELECT_END)]
    need(actual_select.count(b"MaybeUninit::new(") ==
         pins["actual_select_new_call_count"] == 2,
         "actual select no longer has two constructor calls")
    local = (b"pub mod source_copy {\n"
             b"    use std::mem::ManuallyDrop;\n"
             b"    #[repr(transparent)]\n"
             + union_sig + b" " + union_fields + b"\n"
             + impl_sig + b" {\n    " + new_sig + b" " + new_body + b"\n}\n"
             b"}\n")
    external = (b"pub fn external_new_call<T>(val: T) -> std::mem::MaybeUninit<T> {\n"
                b"    std::mem::MaybeUninit::<T>::new(val)\n}\n")
    local_call = (b"pub fn local_new_call<T>(val: T) -> source_copy::MaybeUninit<T> {\n"
                  b"    source_copy::MaybeUninit::<T>::new(val)\n}\n")
    unit = (b"#![feature(transparent_unions)]\n\n"
            + local + b"\n" + local_call + b"\n" + external)
    need(unit.count(union_sig) == 1 and unit.count(new_sig) == 1 and
         unit.count(b"std::mem::MaybeUninit::<T>::new(val)") == 1 and
         b"T: Copy" not in unit and b"T: Freeze" not in unit and
         b"size_of" not in unit and b"on_unwind_ens" not in unit,
         "disposable unit changed generic domain or external call")
    a.evidence.mkdir(parents=True)
    (a.evidence / "verified").mkdir()
    (a.evidence / "original").mkdir()
    (a.evidence / "verified/lib.rs").write_bytes(unit)
    (a.evidence / "original/lib.rs").write_bytes(unit)
    source_record = {
        "classification": "GENERIC_NEW_SOURCE_EQUIVALENCE_CAPTURE_ONLY",
        "accepted": False, "actual_callee_proved": False,
        "provider": provider_identity,
        "proof_head": subprocess.check_output(
            ("git", "-C", str(a.proof_root), "rev-parse", "HEAD"), text=True).strip(),
        "pinned_complete_source_sha256": FILE_SHA,
        "source_pin_manifest_sha256": sha(PINS.read_bytes()),
        "union_signature": union_sig.decode(),
        "union_fields_sha256": sha(union_fields),
        "constructor_signature": new_sig.decode(),
        "constructor_body_sha256": sha(new_body),
        "actual_select_body_excerpt_sha256": sha(actual_select),
        "actual_select_external_new_calls": 2,
        "local_module_sha256": sha(local),
        "local_constructor_runtime_body_exact_from_std": True,
        "local_union_fields_exact_from_std": True,
        "local_copy_defid_differs_from_core": True,
        "external_wrapper_call_unchanged": True,
        "omitted_union_attributes": pins["omitted_union_metadata"],
        "retained_union_attributes": pins["retained_union_metadata"],
        "omitted_method_attributes": pins["omitted_new_metadata"],
        "omitted_source_regions": {
            "method_docs_and_impl_prefix_sha256": sha(std[std.index(impl_sig):
                                                        new_at - 4 - len(NEW_ATTRS)]),
            "all_other_core_items": "excluded; complete source files pinned above",
            "other_maybeuninit_impl_members": "excluded; only new<T> copied",
            "core_only_lang_item_and_derive": "excluded; no actual DefId equivalence",
        },
        "local_import_difference": "std::mem::ManuallyDrop instead of crate::mem import",
        "added_local_crate_attributes": ["#![feature(transparent_unions)]"],
        "added_local_wrappers": ["local_new_call<T>", "external_new_call<T>"],
        "generated_source_sha256": sha(unit),
        "ghost_strip_identity": True,
        "normal_unwind_contract_or_summary": "NOT_PROVIDED",
        "generic_ownership_model": "OPAQUE_UNCHANGED",
    }
    (a.evidence / "source-certificate.json").write_text(
        json.dumps(source_record, indent=2, sort_keys=True) + "\n")
    return source_record


def main() -> None:
    p = argparse.ArgumentParser()
    for name in ("proof-root", "cloud-dir", "evidence"):
        p.add_argument("--" + name, type=Path, required=True)
    prepare(p.parse_args())


if __name__ == "__main__":
    main()
