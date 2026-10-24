#!/usr/bin/env python3
"""Generate the closed, refusal-only W4 contract-input diagnostic patch.

The generator only patches the exact reviewed 5170 translator text and emits a
manifest. It never edits a tool checkout or invokes OCaml/native tools.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from pathlib import Path

BASE_SHA256 = "5170c56386f092d55a42251594eb4b080073f58828cbe1dcf44053b5bdc99942"
R24_PHASE = "SORT4-ACTUAL-SELECT-2026-10-24-R24"
R21_PHASE = "SORT4-ACTUAL-SELECT-2026-10-23-R21"
PROFILE = "experimental-s6-26.10-v1"
SOURCE_SHA256 = "e3fb9d257609d07b8a54afd135d219e6f531fa274364b9671f87e07e93d0d663"
CALLEE_SOURCE_SHA256 = "687327ca06d076d9bf3528859109ff5fc93b21b9cbbab7834d64edac93fbeaff"
CALLEE_UNIT_SHA256 = "cc6292e0683b62b8457267f2963bfb29901d0a5492fa10933c0be9cb2f674925"
CALLEE_BODY_SHA256 = "d370bf5eeeaf553ba450d3add562b85f46673bbac21c249b439ef126443bbb08"
CALLER_UNIT_SHA256 = "b711429f889c6e36393272c29fcc9c4e50fe75beb2ffe2d048ffc424b4325c83"
CALLER_BODY_SHA256 = "067c11f2b290d462d5a203678d069abe53ceffed6362a6ba4cd47035fa81a67e"
QUALIFIED_PROFILE_SHA256 = "a826753d75bbc154d64216e8de6e90ddc10c4b78f8e34b475cca37325d1cf24d"
REFERENCE_HEADER_SHA256 = "5721c3d6daf63769a52a9d158cd00e810832ae51b8279988651b7fe0745df0be"
HEADER_VARIANTS_SHA256 = "c6c0d73db8c263ac0a688b4f18139e98f8c8dbf2581e58fa6558451eaa76630c"
CALL_NAVIGATION_SHA256 = "8d797805c256370660d23b3d725bfefec2ece548a4ca766c2d0ede4b25d9a375"

ENV_NAMES = {
    "MODE": "SORT4_R24_W4_CONTRACT_MODE",
    "CASE": "SORT4_R24_W4_CONTRACT_CASE",
    "EVIDENCE_DIR": "SORT4_R24_W4_CONTRACT_EVIDENCE_DIR",
    "SOURCE_SHA256": "SORT4_R24_W4_CONTRACT_SOURCE_SHA256",
    "CALLEE_UNIT": "SORT4_R24_W4_CONTRACT_CALLEE_UNIT",
    "CALLEE_BODY": "SORT4_R24_W4_CONTRACT_CALLEE_BODY",
    "CALLEE_SOURCE": "SORT4_R24_W4_CONTRACT_CALLEE_SOURCE",
    "REFERENCE_HEADER": "SORT4_R24_W4_CONTRACT_REFERENCE_HEADER",
    "QUALIFIED_PROFILE": "SORT4_R24_W4_CONTRACT_QUALIFIED_PROFILE",
}

CASE_ROWS = {
    "positive": ("5721c3d6daf63769a52a9d158cd00e810832ae51b8279988651b7fe0745df0be", 385),
    "false-normal": ("4f0fcc5f53d5c125080324f14528e95135028226586d762c94417890f4b531c6", 395),
    "false-unwind": ("c460bb95882fab046039af444e3b1322609f6e264a8d49648c842912e9567ba7", 395),
    "duplicate-thread": ("dda95d03fcdf887717ee6a299edf5fc71016ccba191e52b280754369336a742e", 405),
    "mut-pointer": ("f077c50e120a748d7130d8c5a8e5892a8e6e64965e8dd7aa58dd6a20ab39eefd", 383),
    "extra-declaration": ("c0cf3695593322b1eb83c3adfc25e08fa1dd1d1dde3c1fa2cbb99379044c74d0", 476),
}

MODE = {
    "schema": "select-r24-w4-contract-inputs-mode-v1",
    "route": {
        "phase": R24_PHASE,
        "callee_phase": R21_PHASE,
        "owner": "select-sort4",
        "lane": "o26-select-callee-r20",
        "profile": PROFILE,
    },
    "candidate": {
        "verified_source_sha256": SOURCE_SHA256,
        "callee_source_sha256": CALLEE_SOURCE_SHA256,
        "callee_unit_sha256": CALLEE_UNIT_SHA256,
        "callee_body_sha256": CALLEE_BODY_SHA256,
        "caller_unit_sha256": CALLER_UNIT_SHA256,
        "caller_body_sha256": CALLER_BODY_SHA256,
        "qualified_profile_sha256": QUALIFIED_PROFILE_SHA256,
        "reference_header_sha256": REFERENCE_HEADER_SHA256,
        "header_variants_sha256": HEADER_VARIANTS_SHA256,
        "typed_call_navigation_sha256": CALL_NAVIGATION_SHA256,
    },
    "cases": {name: {"header_sha256": sha, "bytes": size} for name, (sha, size) in CASE_ROWS.items()},
    "native_environment": {
        "fixed_mode_value": "1",
        "case_values": list(CASE_ROWS),
        "path_environment_keys": [
            "SORT4_R24_W4_CONTRACT_EVIDENCE_DIR",
            "SORT4_R24_W4_CONTRACT_CALLEE_UNIT",
            "SORT4_R24_W4_CONTRACT_CALLEE_BODY",
            "SORT4_R24_W4_CONTRACT_CALLEE_SOURCE",
            "SORT4_R24_W4_CONTRACT_REFERENCE_HEADER",
            "SORT4_R24_W4_CONTRACT_QUALIFIED_PROFILE",
        ],
        "source_sha256_environment_key": "SORT4_R24_W4_CONTRACT_SOURCE_SHA256",
        "source_sha256": SOURCE_SHA256,
        "extern_spec": "r24_select=<case-pinned .rsspec path>",
    },
    "typed_call_linkage": "UNKNOWN",
    "expected_results": {
        "positive": {
            "exit_code": 1,
            "classification": "INPUTS_MATCH",
            "stderr": "SORT4-R24-W4-CONTRACT-INPUTS: diagnostic refusal: contract inputs matched; no proof rule admitted",
        },
        "false-normal": {"exit_code": 1, "classification": "EXPECTED_INPUT_REFUSAL"},
        "false-unwind": {"exit_code": 1, "classification": "EXPECTED_INPUT_REFUSAL"},
        "duplicate-thread": {"exit_code": 1, "classification": "EXPECTED_INPUT_REFUSAL"},
        "mut-pointer": {"exit_code": 1, "classification": "EXPECTED_INPUT_REFUSAL"},
        "extra-declaration": {"exit_code": 1, "classification": "EXPECTED_INPUT_REFUSAL"},
    },
    "caller_body_proof_admission": False,
    "accepted": False,
    "publication_allowed": False,
    "proof_credit": 0,
}

def expected_mode() -> dict:
    """Return a fresh copy of the canonical closed mode object for integration."""
    return json.loads(json.dumps(MODE))

PROBE = r'''  (* Closed C6 input-congruence diagnostic. It cannot install or consume a
     function summary and always refuses before body translation/proof. *)
  let sort4_r24_w4_contract_inputs_probe (extern_specs : string list)
      (vf_mir_cpn : VfMirRd.VfMir.t) =
    let prefix = "SORT4-R24-W4-CONTRACT-INPUTS: diagnostic refusal: " in
    let reject why = failwith (prefix ^ why) in
    let refuse why = failwith (prefix ^ why) in
    let env k = Sys.getenv_opt ("SORT4_R24_W4_CONTRACT_" ^ k) in
    let allowed = [
      "SORT4_R24_SESSION_PHASE_ID"; "SORT4_R20_CALLEE_PHASE_ID";
      "SORT4_SELECT_PROFILE"; "SORT4_R24_W4_CONTRACT_MODE";
      "SORT4_R24_W4_CONTRACT_CASE"; "SORT4_R24_W4_CONTRACT_EVIDENCE_DIR";
      "SORT4_R24_W4_CONTRACT_SOURCE_SHA256";
      "SORT4_R24_W4_CONTRACT_CALLEE_UNIT";
      "SORT4_R24_W4_CONTRACT_CALLEE_BODY";
      "SORT4_R24_W4_CONTRACT_CALLEE_SOURCE";
      "SORT4_R24_W4_CONTRACT_REFERENCE_HEADER";
      "SORT4_R24_W4_CONTRACT_QUALIFIED_PROFILE"
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
    let valid_uuid = function
      | Some value when String.length value = 36 ->
          let rec loop i =
            if i = 36 then true
            else if i = 8 || i = 13 || i = 18 || i = 23 then
              value.[i] = '-' && loop (i + 1)
            else
              let c = value.[i] in
              ((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')) && loop (i + 1)
          in loop 0
      | _ -> false in
    if Sys.getenv_opt "SMALLSORT_EXECUTION_PROVIDER" <> Some "cloud-build" ||
       Sys.getenv_opt "SORT4_R24_SESSION_PHASE_ID" <>
         Some "SORT4-ACTUAL-SELECT-2026-10-24-R24" ||
       Sys.getenv_opt "SORT4_R20_CALLEE_PHASE_ID" <>
         Some "SORT4-ACTUAL-SELECT-2026-10-23-R21" ||
       Sys.getenv_opt "SORT4_SELECT_PROFILE" <> Some "experimental-s6-26.10-v1" ||
       Sys.getenv_opt "LANE" <> Some "o26-select-callee-r20" ||
       not (valid_uuid (Sys.getenv_opt "CLOUD_BUILD_ID")) ||
       Sys.getenv_opt "GITHUB_ACTIONS" <> None || env "MODE" <> Some "1" then
      reject "exact R24/R21/profile/provider/lane route required";
    let case = match env "CASE" with
      | Some ("positive" | "false-normal" | "false-unwind" |
              "duplicate-thread" | "mut-pointer" | "extra-declaration" as c) -> c
      | _ -> reject "closed contract-input case required" in
    let no_symlink_path path want_dir =
      let rec check p =
        let st = Unix.lstat p in
        let good = if p = path then
          (if want_dir then st.Unix.st_kind = Unix.S_DIR
           else st.Unix.st_kind = Unix.S_REG)
          else st.Unix.st_kind <> Unix.S_LNK in
        if not good then false else
        let parent = Filename.dirname p in parent = p || check parent
      in try check path with Unix.Unix_error _ -> false in
    let read_regular path =
      if Filename.is_relative path || not (no_symlink_path path false) then
        reject "absolute regular nonsymlink input required";
      let ch = open_in_bin path in
      Fun.protect ~finally:(fun () -> close_in ch)
        (fun () -> really_input_string ch (in_channel_length ch)) in
    let hash s = sort4_actual_owner_sha256 s in
    let path_of key = match env key with
      | Some p when p <> "" -> p | _ -> reject ("missing " ^ key ^ " path") in
    let evidence = path_of "EVIDENCE_DIR" in
    if Filename.is_relative evidence || not (no_symlink_path evidence true) ||
       Array.length (Sys.readdir evidence) <> 0 then
      reject "absolute fresh nonsymlink evidence directory required";
    let expected_source = "e3fb9d257609d07b8a54afd135d219e6f531fa274364b9671f87e07e93d0d663" in
    if env "SOURCE_SHA256" <> Some expected_source then
      reject "exact W4 verified-source SHA256 required";
    let reference_header = read_regular (path_of "REFERENCE_HEADER") in
    if hash reference_header <> "5721c3d6daf63769a52a9d158cd00e810832ae51b8279988651b7fe0745df0be" then
      reject "exact positive reference header required";
    let profile = read_regular (path_of "QUALIFIED_PROFILE") in
    if hash profile <> "a826753d75bbc154d64216e8de6e90ddc10c4b78f8e34b475cca37325d1cf24d" then
      reject "exact qualified current-profile receipt required";
    let callee_source_path = path_of "CALLEE_SOURCE" in
    let callee_source = read_regular callee_source_path in
    if hash callee_source <> "687327ca06d076d9bf3528859109ff5fc93b21b9cbbab7834d64edac93fbeaff" then
      reject "exact verified select_unpredictable source required";
    if not (Filename.check_suffix callee_source_path
              (Filename.concat "verified" "lib.rs")) then
      reject "provided callee source path must end in verified/lib.rs";
    let callee_unit_bytes = read_regular (path_of "CALLEE_UNIT") in
    let callee_body_bytes = read_regular (path_of "CALLEE_BODY") in
    if hash callee_unit_bytes <> "cc6292e0683b62b8457267f2963bfb29901d0a5492fa10933c0be9cb2f674925" ||
       hash callee_body_bytes <> "d370bf5eeeaf553ba450d3add562b85f46673bbac21c249b439ef126443bbb08" then
      reject "same-run qualified callee unit/body bytes mismatch";
    let callee_unit : D.vf_mir = Marshal.from_string callee_unit_bytes 0 in
    let callee_body : D.body = Marshal.from_string callee_body_bytes 0 in
    let callee_bodies = callee_unit.bodies in
    if List.length callee_bodies <> 9 ||
       callee_body.def_path <> "select_unpredictable" then
      reject "callee body is not qualified unit body 7";
    let unit_body7_bytes = Marshal.to_string (List.nth callee_bodies 7) [Marshal.No_sharing] in
    if unit_body7_bytes <> callee_body_bytes then
      reject "provided callee body bytes are not body 7 of the provided unit";
    let* callee_sig_loc = translate_decoded_span_data callee_body.fn_sig_span in
    let mir_callee_source_path = match callee_sig_loc with
     | Ast.Lexed (((p,_,_), (q,_,_))) when p = q &&
          (if Filename.is_relative p then p = "verified/lib.rs"
           else Unix.realpath p = Unix.realpath callee_source_path) ->
          if Filename.is_relative p then callee_source_path else p
     | _ -> reject "callee body signature must identify verified/lib.rs" in
    let mir_callee_source = read_regular mir_callee_source_path in
    if hash mir_callee_source <> "687327ca06d076d9bf3528859109ff5fc93b21b9cbbab7834d64edac93fbeaff" then
      reject "callee MIR signature source does not match qualified source";
    let* actual_callee_loc = translate_decoded_span_data callee_body.contract.span in
    let* actual_annots = ListAux.try_map (fun (a : D.annotation) ->
      let* span = translate_decoded_span_data a.span in
      let annot : Mir.annot = { span; raw = a.raw } in
      Ok (translate_annot_to_vf_parser_inp annot))
      callee_body.contract.annotations in
    let ((_, (_, _safety_proof), pre_post, terminates), assume_correct) =
      VfMirAnnotParser.parse_func_contract actual_callee_loc actual_annots in
    if assume_correct || terminates then reject "actual contract has forbidden assume/terminates clause";
    let actual_spec = match pre_post with
      | Some spec -> spec | None -> reject "actual callee contract missing" in
    let actual_contract =
      Ocaml_expr_formatter.string_of_ocaml_expr true
        (Ocaml_expr_of_ast.of_spec actual_spec) in
    let header_path, header_bytes = match extern_specs with
      | [arg] -> (match String.split_on_char '=' arg with
          | ["r24_select"; p] -> p, read_regular p
          | _ -> reject "only the r24_select external header is permitted")
      | _ -> reject "exactly one r24_select external header is required" in
    let expected_header = match case with
      | "positive" -> "5721c3d6daf63769a52a9d158cd00e810832ae51b8279988651b7fe0745df0be"
      | "false-normal" -> "4f0fcc5f53d5c125080324f14528e95135028226586d762c94417890f4b531c6"
      | "false-unwind" -> "c460bb95882fab046039af444e3b1322609f6e264a8d49648c842912e9567ba7"
      | "duplicate-thread" -> "dda95d03fcdf887717ee6a299edf5fc71016ccba191e52b280754369336a742e"
      | "mut-pointer" -> "f077c50e120a748d7130d8c5a8e5892a8e6e64965e8dd7aa58dd6a20ab39eefd"
      | _ -> "c0cf3695593322b1eb83c3adfc25e08fa1dd1d1dde3c1fa2cbb99379044c74d0" in
    let expected_header_size = match case with
      | "positive" -> 385 | "false-normal" | "false-unwind" -> 395
      | "duplicate-thread" -> 405 | "mut-pointer" -> 383
      | _ -> 476 in
    if String.length header_bytes <> expected_header_size ||
       hash header_bytes <> expected_header then
      reject "case header bytes do not match the closed variant pin";
    let decls = VfMirAnnotParser.parse_rsspec_file header_path in
    let contains_text haystack needle =
      let n = String.length needle in
      let rec at i =
        i + n <= String.length haystack &&
        (String.sub haystack i n = needle || at (i + 1))
      in at 0 in
    let header_spec = match decls with
      | [Ast.Func (_, Ast.Regular, ["Element", {Ast.sized=true}],
          Some (Ast.ConstructedTypeExpr (_, "fn_outcome",
            [Ast.PtrTypeExpr (_, Ast.IdentTypeExpr (_, None, "Element"))])),
          "select_unpredictable_const",
          [(Ast.ManifestTypeExpr (_, Ast.Bool), "condition");
           (Ast.PtrTypeExpr (_, Ast.IdentTypeExpr (_, None, "Element")), "true_val");
           (Ast.PtrTypeExpr (_, Ast.IdentTypeExpr (_, None, "Element")), "false_val")],
          false, (None, None), Some spec, false, None, false, [])]
          when case <> "mut-pointer" -> Some spec
      | [Ast.Func (_, Ast.Regular, _, _, "select_unpredictable_const", _, _, _, _, _, _, _, _)]
          when case = "mut-pointer" &&
               contains_text header_bytes "true_val: *mut Element," -> None
      | [Ast.Func (_, Ast.Regular, _, _, "select_unpredictable_const", _, _, _, _, _, _, _, _);
         Ast.Func (_, Ast.Regular, _, _, "extra_unchecked_summary", _, _, _, _, _, _, _, _)]
          when case = "extra-declaration" -> None
      | _ -> reject "header must be the exact one-function Element/pointer specialization" in
    let imported_contract = match header_spec with
      | Some spec -> Ocaml_expr_formatter.string_of_ocaml_expr true
          (Ocaml_expr_of_ast.of_spec spec)
      | None -> "" in
    let body_bytes = Marshal.to_string (D.decode_body
      (List.hd (VfMirRd.VfMir.bodies_get_list vf_mir_cpn))) [Marshal.No_sharing] in
    let unit_bytes = Marshal.to_string (D.decode_vf_mir vf_mir_cpn) [Marshal.No_sharing] in
    if hash unit_bytes <> "b711429f889c6e36393272c29fcc9c4e50fe75beb2ffe2d048ffc424b4325c83" ||
       hash body_bytes <> "067c11f2b290d462d5a203678d069abe53ceffed6362a6ba4cd47035fa81a67e" then
      reject "W4 caller unit/body differs from the exact eight-call input capture";
    let caller_bodies = VfMirRd.VfMir.bodies_get_list vf_mir_cpn in
    (match caller_bodies with
     | [b] when TrName.translate_def_path (BodyRd.def_path_get b) = "sort4_stable" -> ()
     | _ -> reject "exact one-body sort4_stable caller inventory required");
    let* caller_span = translate_span_data (BodyRd.fn_sig_span_get (List.hd caller_bodies)) in
    let caller_source_path = match caller_span with
      | Ast.Lexed (((p,_,_), (q,_,_))) when p = q &&
          (if Filename.is_relative p then p = "verified/lib.rs"
           else Filename.check_suffix p (Filename.concat "verified" "lib.rs")) ->
          if Filename.is_relative p then Filename.concat (Sys.getcwd ()) p else p
      | _ -> reject "W4 caller signature must name verified/lib.rs" in
    let caller_source = read_regular caller_source_path in
    if hash caller_source <> expected_source then
      reject "exact current W4 source bytes required";
    let specs_equal = actual_contract = imported_contract in
    let expected_match = case = "positive" in
    let shape_ok = match case, header_spec with
      | "mut-pointer", None -> true
      | "extra-declaration", None -> true
      | _, Some _ -> true
      | _ -> false in
    if not shape_ok then reject "header declaration shape mismatch";
    if specs_equal <> expected_match then
      reject "actual and imported weak contracts do not have the expected equality result";
    let actual_path = Filename.concat evidence "actual-contract.ml" in
    let imported_path = Filename.concat evidence "imported-contract.ml" in
    let facts_path = Filename.concat evidence "contract-inputs.json" in
    let absent p = try ignore (Unix.lstat p); false
      with Unix.Unix_error (Unix.ENOENT,_,_) -> true in
    if not (absent actual_path && absent imported_path && absent facts_path) then
      reject "diagnostic output already exists";
    let write_excl path data =
      let ch = open_out_gen [Open_wronly; Open_creat; Open_excl; Open_binary] 0o600 path in
      Fun.protect ~finally:(fun () -> close_out ch) (fun () -> output_string ch data) in
    let actual_bytes = actual_contract ^ "\n" in
    let imported_bytes = imported_contract ^ "\n" in
    write_excl actual_path actual_bytes;
    write_excl imported_path imported_bytes;
    let j s =
      let b = Buffer.create (String.length s + 8) in
      Buffer.add_char b '"'; String.iter (function
        | '"' -> Buffer.add_string b "\\\""
        | '\\' -> Buffer.add_string b "\\\\"
        | '\n' -> Buffer.add_string b "\\n"
        | '\r' -> Buffer.add_string b "\\r"
        | '\t' -> Buffer.add_string b "\\t"
        | c when Char.code c < 32 -> Buffer.add_string b (Printf.sprintf "\\u%04x" (Char.code c))
        | c -> Buffer.add_char b c) s;
      Buffer.add_char b '"'; Buffer.contents b in
    let input path bytes = Printf.sprintf
      "{\"path\":%s,\"bytes\":%d,\"sha256\":%s}"
      (j path) (String.length bytes) (j (hash bytes)) in
    let memory_input bytes = Printf.sprintf
      "{\"origin\":\"native_input\",\"bytes\":%d,\"sha256\":%s}"
      (String.length bytes) (j (hash bytes)) in
    let record = Printf.sprintf
      "{\"schema\":\"select-r24-w4-contract-inputs-v1\",\"case\":%s,\"complete\":true,\"classification\":%s,\"expected_refusal\":%s,\"inputs\":{\"caller_source\":%s,\"caller_unit\":%s,\"caller_body\":%s,\"callee_source\":%s,\"callee_source_in_mir\":%s,\"callee_unit\":%s,\"callee_body\":%s,\"reference_header\":%s,\"variant_header\":%s,\"qualified_profile\":%s},\"actual_contract\":{\"path\":\"actual-contract.ml\",\"bytes\":%d,\"sha256\":%s},\"imported_contract\":{\"path\":\"imported-contract.ml\",\"bytes\":%d,\"sha256\":%s},\"typed_call_navigation_sha256\":\"8d797805c256370660d23b3d725bfefec2ece548a4ca766c2d0ede4b25d9a375\",\"typed_call_site_count_source_reported\":8,\"typed_call_linkage\":\"UNKNOWN\",\"caller_body_proof_admission\":false,\"accepted\":false,\"publication_allowed\":false,\"proof_credit\":0}\n"
      (j case) (j (if expected_match then "INPUTS_MATCH" else "EXPECTED_INPUT_REFUSAL"))
      (j (if expected_match then "contract inputs matched; no proof rule admitted" else "exact pinned control contract rejected"))
      (input caller_source_path caller_source) (memory_input unit_bytes)
      (memory_input body_bytes)
      (input (path_of "CALLEE_SOURCE") callee_source)
      (input mir_callee_source_path mir_callee_source)
      (input (path_of "CALLEE_UNIT") callee_unit_bytes)
      (input (path_of "CALLEE_BODY") callee_body_bytes)
      (input (path_of "REFERENCE_HEADER") reference_header)
      (input header_path header_bytes)
      (input (path_of "QUALIFIED_PROFILE") profile)
      (String.length actual_bytes) (j (hash actual_bytes))
      (String.length imported_bytes) (j (hash imported_bytes)) in
    write_excl facts_path record;
    Printf.printf "SORT4-R24-W4-CONTRACT-INPUTS: case=%s actual_spec_sha256=%s imported_spec_sha256=%s caller_body_sha256=%s typed_call_linkage=UNKNOWN\n%!"
      case (hash actual_bytes) (hash imported_bytes) (hash body_bytes);
    refuse (if expected_match then "contract inputs matched; no proof rule admitted"
            else "pinned control contract refused; no proof rule admitted")
'''

DISPATCH = r'''      let contract_env_keys = [
        "SORT4_R24_W4_CONTRACT_MODE"; "SORT4_R24_W4_CONTRACT_CASE";
        "SORT4_R24_W4_CONTRACT_EVIDENCE_DIR";
        "SORT4_R24_W4_CONTRACT_SOURCE_SHA256";
        "SORT4_R24_W4_CONTRACT_CALLEE_UNIT";
        "SORT4_R24_W4_CONTRACT_CALLEE_BODY";
        "SORT4_R24_W4_CONTRACT_CALLEE_SOURCE";
        "SORT4_R24_W4_CONTRACT_REFERENCE_HEADER";
        "SORT4_R24_W4_CONTRACT_QUALIFIED_PROFILE"
      ] in
      Array.iter (fun binding ->
        match String.index_opt binding '=' with
        | None -> failwith
            "SORT4-R24-W4-CONTRACT-INPUTS: diagnostic refusal: malformed process environment entry"
        | Some equals ->
            let key = String.sub binding 0 equals in
            let prefix = "SORT4_R24_W4_CONTRACT_" in
            if String.length key >= String.length prefix &&
               String.sub key 0 (String.length prefix) = prefix &&
               not (List.mem key contract_env_keys) then
              failwith
                ("SORT4-R24-W4-CONTRACT-INPUTS: diagnostic refusal: foreign contract mode key: " ^ key))
        (Unix.environment ());
      let* () = match
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_MODE",
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_CASE",
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_EVIDENCE_DIR",
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_SOURCE_SHA256",
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_CALLEE_UNIT",
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_CALLEE_BODY",
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_CALLEE_SOURCE",
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_REFERENCE_HEADER",
          Sys.getenv_opt "SORT4_R24_W4_CONTRACT_QUALIFIED_PROFILE" with
        | None, None, None, None, None, None, None, None, None -> Ok ()
        | Some _, Some _, Some _, Some _, Some _, Some _, Some _, Some _, Some _ ->
            sort4_r24_w4_contract_inputs_probe extern_specs vf_mir_cpn
        | _ -> failwith
            "SORT4-R24-W4-CONTRACT-INPUTS: diagnostic refusal: partial environment"
      in
'''

PROBE_ANCHOR = "  let translate_vf_mir (extern_specs : string list)\n      (vf_mir_cpn : VfMirRd.VfMir.t) =\n"
DISPATCH_ANCHOR = '      let* () = match\n          Sys.getenv_opt "SORT4_R24_W4_FINGERPRINT_MODE",\n'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def generate(base: bytes) -> bytes:
    if sha(base) != BASE_SHA256:
        raise ValueError("translator base SHA does not match exact 5170 source")
    text = base.decode("utf-8", "strict")
    if text.count(PROBE_ANCHOR) != 1 or text.count(DISPATCH_ANCHOR) != 1:
        raise ValueError("unique probe/dispatch insertion anchors required")
    text = text.replace(PROBE_ANCHOR, PROBE + "\n" + PROBE_ANCHOR, 1)
    text = text.replace(DISPATCH_ANCHOR, DISPATCH + DISPATCH_ANCHOR, 1)
    result = text.encode("utf-8")
    if result == base or text.count("sort4_r24_w4_contract_inputs_probe") != 2:
        raise ValueError("diagnostic insertion did not produce expected source")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--patch-output", type=Path, default=(Path(__file__).parents[2] / "cloud-build/sort4-caller-entry-native/w4-contract-input-r24.patch"))
    parser.add_argument("--manifest-output", type=Path, default=(Path(__file__).with_name("W4-CONTRACT-INPUT-MANIFEST.json")))
    args = parser.parse_args()
    base = args.base.read_bytes()
    patched = generate(base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(patched)
    patch = "".join(difflib.unified_diff(
        base.decode().splitlines(keepends=True), patched.decode().splitlines(keepends=True),
        fromfile="a/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
        tofile="b/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml", n=3))
    args.patch_output.parent.mkdir(parents=True, exist_ok=True)
    args.patch_output.write_text(patch, encoding="utf-8")
    manifest = {
        "schema": "select-r24-w4-contract-input-manifest-v1",
        "state": "GENERATED_DIAGNOSTIC_ONLY_REVIEW_PENDING",
        "base_translator_sha256": BASE_SHA256,
        "result_translator_sha256": sha(patched),
        "generator_sha256": sha(Path(__file__).read_bytes()),
        "patch": {
            "path": "research/challenge-8/cloud-build/sort4-caller-entry-native/w4-contract-input-r24.patch",
            "sha256": sha(patch.encode()),
        },
        "mode": MODE,
        "native_inputs": {
            "source_sha256": SOURCE_SHA256,
            "caller_unit_sha256": CALLER_UNIT_SHA256,
            "caller_body_sha256": CALLER_BODY_SHA256,
            "callee_source_sha256": CALLEE_SOURCE_SHA256,
            "callee_unit_sha256": CALLEE_UNIT_SHA256,
            "callee_body_sha256": CALLEE_BODY_SHA256,
            "qualified_profile_sha256": QUALIFIED_PROFILE_SHA256,
            "reference_header_sha256": REFERENCE_HEADER_SHA256,
            "header_variants_sha256": HEADER_VARIANTS_SHA256,
            "typed_call_navigation_sha256": CALL_NAVIGATION_SHA256,
        },
        "header_cases": {name: {"sha256": sha_, "bytes": size} for name, (sha_, size) in CASE_ROWS.items()},
        "outputs": ["contract-inputs.json", "actual-contract.ml", "imported-contract.ml"],
        "diagnostic": "All configured cases fail closed before body translation/proof; matching inputs do not install or consume a summary.",
        "typed_call_linkage": "UNKNOWN",
        "caller_body_proof_admission": False,
        "accepted": False,
        "publication_allowed": False,
        "proof_credit": 0,
    }
    args.manifest_output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"base_sha256={BASE_SHA256}")
    print(f"result_sha256={sha(patched)}")
    print(f"patch_sha256={sha(patch.encode())}")
    print(f"manifest={args.manifest_output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
