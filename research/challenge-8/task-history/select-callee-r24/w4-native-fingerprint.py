#!/usr/bin/env python3
"""Generate the closed R24 W4 refusal-only native Marshal probe overlay.

The generator reads one pinned translator snapshot, checks its exact bytes,
applies two unique textual insertions, and emits a disposable patched source
plus a unified patch. It never modifies a tool checkout or runs a compiler.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
from pathlib import Path
import sys


BASE_SHA256 = '8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007'
SOURCE_SHA256 = 'e3fb9d257609d07b8a54afd135d219e6f531fa274364b9671f87e07e93d0d663'
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
PROFILE = 'experimental-s6-26.10-v1'
MODE = 'SORT4_R24_W4_FINGERPRINT_MODE'
EVIDENCE = 'SORT4_R24_W4_FINGERPRINT_EVIDENCE_DIR'
SOURCE_HASH = 'SORT4_R24_W4_FINGERPRINT_SOURCE_SHA256'


PROBE = r'''  (* Closed R24 W4 native representation capture. This mode always refuses
     after writing its two Marshal snapshots and cannot admit a proof rule. *)
  let sort4_r24_w4_fingerprint_probe (vf_mir : VfMirRd.VfMir.t) =
    let reject why = failwith
      ("SORT4-R24-W4-FINGERPRINT: diagnostic refusal: " ^ why) in
    let allowed = [
      "SORT4_R24_SESSION_PHASE_ID";
      "SORT4_R20_CALLEE_PHASE_ID";
      "SORT4_SELECT_PROFILE";
      "SORT4_R24_W4_FINGERPRINT_MODE";
      "SORT4_R24_W4_FINGERPRINT_EVIDENCE_DIR";
      "SORT4_R24_W4_FINGERPRINT_SOURCE_SHA256"
    ] in
    Array.iter (fun binding ->
      match String.index_opt binding '=' with
      | None -> reject "malformed process environment entry"
      | Some equals ->
          let key = String.sub binding 0 equals in
          if String.length key >= 6 && String.sub key 0 6 = "SORT4_" &&
             not (List.mem key allowed) then
            reject ("foreign SORT4 environment key: " ^ key))
      (Unix.environment ());
    if Sys.getenv_opt "SMALLSORT_EXECUTION_PROVIDER" <> Some "cloud-build" ||
       Sys.getenv_opt "SORT4_R24_SESSION_PHASE_ID" <>
         Some "SORT4-ACTUAL-SELECT-2026-10-24-R24" ||
       Sys.getenv_opt "SORT4_R20_CALLEE_PHASE_ID" <>
         Some "SORT4-ACTUAL-SELECT-2026-10-23-R21" ||
       Sys.getenv_opt "SORT4_SELECT_PROFILE" <>
         Some "experimental-s6-26.10-v1" ||
       Sys.getenv_opt "LANE" <> Some "o26-select-callee-r20" ||
       Sys.getenv_opt "CLOUD_BUILD_ID" = None ||
       Sys.getenv_opt "GITHUB_ACTIONS" <> None ||
       Sys.getenv_opt "SORT4_R24_W4_FINGERPRINT_MODE" <> Some "1" then
      reject "exact R24/R21/profile/provider/lane fingerprint route required";
    let no_symlink_directory path =
      let rec check current =
        if (Unix.lstat current).Unix.st_kind <> Unix.S_DIR then false
        else
          let parent = Filename.dirname current in
          parent = current || check parent in
      try check path with Unix.Unix_error _ -> false in
    let dir = match Sys.getenv_opt
        "SORT4_R24_W4_FINGERPRINT_EVIDENCE_DIR" with
      | Some path when not (Filename.is_relative path) &&
          Sys.file_exists path && Sys.is_directory path &&
          no_symlink_directory path -> path
      | _ -> reject "absolute nonsymlink evidence directory required" in
    let expected_source = match Sys.getenv_opt
        "SORT4_R24_W4_FINGERPRINT_SOURCE_SHA256" with
      | Some hash when hash =
          "e3fb9d257609d07b8a54afd135d219e6f531fa274364b9671f87e07e93d0d663" -> hash
      | _ -> reject "exact captured W4 verified source SHA256 required" in
    let bodies = VfMirRd.VfMir.bodies_get_list vf_mir in
    let named = List.mapi (fun index body ->
      index, body,
      TrName.translate_def_path (BodyRd.def_path_get body)) bodies in
    let source_index, body = match named with
      | [(0, body, "sort4_stable")] -> 0, body
      | _ -> reject "exact one-body sort4_stable unit inventory required" in
    let* signature_span = translate_span_data (BodyRd.fn_sig_span_get body) in
    let source_path = match signature_span with
      | Ast.Lexed (((path, _, _), (last_path, _, _)))
        when path = last_path && Filename.check_suffix path "verified/lib.rs" -> path
      | _ -> reject "sort4_stable signature must name verified/lib.rs" in
    if sort4_actual_owner_sha256 (Sort4MaybeUninit.read_file source_path) <>
         expected_source || expected_source <>
         "e3fb9d257609d07b8a54afd135d219e6f531fa274364b9671f87e07e93d0d663" then
      reject "verified W4 source bytes differ";
    let unit_path = Filename.concat dir "w4-native-unit.marshal" in
    let body_path = Filename.concat dir "w4-native-body-0.marshal" in
    let absent path =
      try ignore (Unix.lstat path); false
      with Unix.Unix_error (Unix.ENOENT, _, _) -> true in
    if not (absent unit_path && absent body_path) then
      reject "fingerprint output already exists";
    let dump path label value =
      let bytes = Marshal.to_string value [Marshal.No_sharing] in
      let channel = open_out_gen
        [Open_wronly; Open_creat; Open_excl; Open_binary] 0o600 path in
      Fun.protect ~finally:(fun () -> close_out channel) (fun () ->
        output_string channel bytes);
      Printf.printf
        "SORT4-R24-W4-FINGERPRINT: %s bytes=%d sha256=%s body_index=%d\n%!"
        label (String.length bytes) (sort4_actual_owner_sha256 bytes) source_index in
    dump unit_path "unit" (D.decode_vf_mir vf_mir);
    dump body_path "sort4_stable-body" (D.decode_body body);
    reject "snapshot complete; no proof rule admitted"

'''

DISPATCH = r'''      let* () = match
          Sys.getenv_opt "SORT4_R24_W4_FINGERPRINT_MODE",
          Sys.getenv_opt "SORT4_R24_W4_FINGERPRINT_EVIDENCE_DIR",
          Sys.getenv_opt "SORT4_R24_W4_FINGERPRINT_SOURCE_SHA256" with
        | None, None, None -> Ok ()
        | Some _, Some _, Some _ ->
            sort4_r24_w4_fingerprint_probe vf_mir_cpn
        | _ -> failwith
            "SORT4-R24-W4-FINGERPRINT: diagnostic refusal: partial environment"
      in
'''

PROBE_ANCHOR = '    reject "snapshot complete; no proof rule admitted"\n\n'
DISPATCH_ANCHOR = '      let* () = match Sys.getenv_opt "SORT4_NESTED_FINGERPRINT_MODE" with\n'


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def generate(base: bytes) -> bytes:
    if digest(base) != BASE_SHA256:
        raise ValueError('translator base SHA does not match pinned 8a026 source')
    try:
        text = base.decode('utf-8', errors='strict')
    except UnicodeDecodeError as exc:
        raise ValueError('translator base is not strict UTF-8') from exc
    if text.count(PROBE_ANCHOR) != 1:
        raise ValueError('fingerprint probe insertion anchor is not unique')
    if text.count(DISPATCH_ANCHOR) != 1:
        raise ValueError('pre-admission dispatch insertion anchor is not unique')
    text = text.replace(PROBE_ANCHOR, PROBE_ANCHOR + PROBE, 1)
    text = text.replace(DISPATCH_ANCHOR, DISPATCH + DISPATCH_ANCHOR, 1)
    result = text.encode('utf-8')
    if result == base or b'let sort4_r24_w4_fingerprint_probe' not in result or \
            b'SORT4_R24_W4_FINGERPRINT_MODE' not in result:
        raise ValueError('generated source does not contain expected probe markers')
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True,
                        help='translator file with exact pinned 8a026 bytes')
    parser.add_argument('--output', type=Path, required=True,
                        help='disposable patched translator output path')
    parser.add_argument('--patch-output', type=Path,
                        default=(Path(__file__).parents[2] /
                                 'cloud-build/sort4-caller-entry-native/'
                                 'w4-native-fingerprint-r24.patch'))
    args = parser.parse_args(argv)
    base = args.base.read_bytes()
    result = generate(base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(result)
    patch = ''.join(difflib.unified_diff(
        base.decode('utf-8').splitlines(keepends=True),
        result.decode('utf-8').splitlines(keepends=True),
        fromfile='a/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',
        tofile='b/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',
        n=3))
    args.patch_output.parent.mkdir(parents=True, exist_ok=True)
    args.patch_output.write_text(patch, encoding='utf-8')
    print('base_sha256=' + digest(base))
    print('result_sha256=' + digest(result))
    print('patch_sha256=' + digest(patch.encode('utf-8')))
    print('output=' + str(args.output))
    print('patch=' + str(args.patch_output))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print('W4-NATIVE-FINGERPRINT-GENERATOR: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
