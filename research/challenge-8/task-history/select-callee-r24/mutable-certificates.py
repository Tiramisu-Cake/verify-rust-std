#!/usr/bin/env python3
"""Generate the closed R24 mutable certificate fragment from pinned JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
FROZEN_TRANSLATOR = Path("/tmp/r24-translator-c8.ml")
FROZEN_TRANSLATOR_SHA256 = (
    "c8f5ce1da4f88a4b029b8ed12cc7667a0e227836b1843a1590f78769e073201e"
)
CAPTURE_PINS = HERE / "P2-MUT-CAPTURE-PINS.json"
CAPTURE_PINS_SHA256 = (
    "b10d8f472fd9babc5e73cb7a8da14ad691b0563975d0d6d956366165a47401d0"
)
MATRIX_PINS = HERE / "P2-MUT-MATRIX-PINS.json"
MATRIX_PINS_SHA256 = (
    "5aee793196c2e0ab5960f1c0ea4aab8880ca68e61d74876363e2ccf3febadbed"
)
OUT = Path("/tmp/r24-mut-certificates.ml.fragment")

VARIANTS = (
    "positive",
    "omit-selected-own",
    "omit-unselected-own",
    "no-retained-half",
    "callee-false-normal",
    "callee-owner-duplicate",
    "callee-owner-loss",
    "callee-thread-duplicate",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def load_pins() -> tuple[dict, dict]:
    if sha(FROZEN_TRANSLATOR) != FROZEN_TRANSLATOR_SHA256:
        raise SystemExit("frozen C8 translator SHA256 mismatch")
    if sha(CAPTURE_PINS) != CAPTURE_PINS_SHA256:
        raise SystemExit("positive mutable capture pins SHA256 mismatch")
    if sha(MATRIX_PINS) != MATRIX_PINS_SHA256:
        raise SystemExit("mutable matrix pins SHA256 mismatch")
    capture = json.loads(CAPTURE_PINS.read_text(encoding="utf-8"))
    matrix = json.loads(MATRIX_PINS.read_text(encoding="utf-8"))
    if capture.get("source", {}).get("contract_text_sha256") != (
        "dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870"
    ):
        raise SystemExit("mutable positive contract hash mismatch")
    if tuple(matrix.get("variant_order", ())) != VARIANTS:
        raise SystemExit("mutable matrix variant order mismatch")
    if set(matrix.get("cases", {})) != set(VARIANTS):
        raise SystemExit("mutable matrix case set mismatch")
    if matrix.get("source", {}).get("original_sha256") != (
        "3bf0bf792c8135bf964f19b3aaadef38b8ca5ee9ec95107029ad99d28a807aaa"
    ):
        raise SystemExit("mutable original source hash mismatch")
    if matrix.get("accepted") is not False or matrix.get("proof_credit") != 0:
        raise SystemExit("mutable matrix pins must remain source-only")
    return capture, matrix


def rows(capture: dict, matrix: dict) -> tuple[str, str]:
    fixed = capture["snapshots"]
    fixed_rows = []
    per_case_rows = []
    for index in (*range(6), 8):
        item = fixed[f"body-{index}"]
        fixed_rows.append(
            f"      ({index}, {quoted(item['sha256'])})"
        )
    for variant in VARIANTS:
        case = matrix["cases"][variant]
        source = case["source"]
        snapshot = case["snapshots"]
        expected = [variant, source["verified_sha256"]]
        expected.extend(
            snapshot[key]["sha256"] for key in ("unit", "body-6", "body-7")
        )
        if source["original_sha256"] != capture["source"]["original_sha256"]:
            raise SystemExit(f"{variant}: mutable original source hash differs")
        per_case_rows.append("      (" + ", ".join(quoted(v) for v in expected) + ")")
    return ";\n".join(fixed_rows), ";\n".join(per_case_rows)


TEMPLATE = r'''(* Generated from the R24 mutable capture and matrix pin manifests.
   Insert after sort4_actual_owner_sha256 and before sort4_actual_owner_admit.
   This module adds only exact source/MIR identity and mutable-shape admission;
   translation hooks and ordinary proof obligations remain in their own code. *)
module Sort4MutCertificate = struct
  let active = ref false
  let case = ref None
  let pointer_drop_redirects = ref 0
  let assume_init_redirects = ref 0
  let select_ptr_calls = ref 0
  let select_wrapper_calls = ref 0
  let forget_redirects = ref 0
  let reject why = failwith
    ("SORT4-R24-MUTABLE-CERTIFICATES: refusal: " ^ why)

  let variants = [
    "positive"; "omit-selected-own"; "omit-unselected-own";
    "no-retained-half"; "callee-false-normal";
    "callee-owner-duplicate"; "callee-owner-loss";
    "callee-thread-duplicate"
  ]

  (* Keep inherited R21/R24 prerequisites private to this closed route.
     This getter is never installed into process-global Sys.getenv. *)
  let derived_legacy_env key selected root =
    match key with
    | "SORT4_ACTUAL_OWNER_REPO_ROOT"
    | "SORT4_ACTUAL_NESTED_H2_REPO_ROOT"
    | "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT"
    | "SORT4_A1_NINE_REPO_ROOT" -> Some root
    | "SORT4_ACTUAL_OWNER_ADMISSION"
    | "SORT4_ACTUAL_OWNER_NINE_ADMISSION"
    | "SORT4_R20_FINAL_SELECT_REPAIR"
    | "SORT4_R21_FRACTIONAL_FORGET" -> Some "1"
    | "SORT4_R21_FRACTIONAL_VARIANT" -> Some selected
    | _ -> None

  let forbidden_legacy_keys = [
    "SORT4_ACTUAL_OWNER_REPO_ROOT"; "SORT4_ACTUAL_OWNER_ADMISSION";
    "SORT4_ACTUAL_OWNER_NINE_ADMISSION";
    "SORT4_ACTUAL_NESTED_H2_REPO_ROOT";
    "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT"; "SORT4_A1_NINE_REPO_ROOT";
    "SORT4_A1_LINK_REPO_ROOT"; "SORT4_POINTER_DROP_REPO_ROOT";
    "SORT4_SELECT_INTRINSIC_REPO_ROOT"; "SORT4_MAYBEUNINIT_REPO_ROOT";
    "SORT4_AS_MUT_PTR_REPO_ROOT"; "SORT4_GUARD_REPO_ROOT";
    "SORT4_GUARD_TEMPLATE_REPO_ROOT"; "SORT4_G1_CALL_REPO_ROOT";
    "SORT4_R20_FINAL_SELECT_REPAIR"; "SORT4_R21_FRACTIONAL_FORGET";
    "SORT4_R21_FRACTIONAL_VARIANT";
    "SORT4_R24_CHECKED_POINTER_OUTCOMES"
  ]

  let fixed_body_hashes = [
__FIXED_ROWS__
  ]

  (* variant, verified source SHA256, complete decoded unit SHA256,
     decoded body-6 SHA256, decoded body-7 SHA256. *)
  let case_hashes = [
__CASE_ROWS__
  ]

  let case_row selected =
    match List.find_opt (fun (name,_,_,_,_) -> name = selected) case_hashes with
    | Some row -> row
    | None -> reject "unknown mutable case"

  let is_hex_sha value =
    String.length value = 64 &&
    String.for_all (fun c ->
      (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')) value

  let exact_env key value = Sys.getenv_opt key = Some value

  let reject_ambient_legacy () =
    List.iter (fun key ->
      if Sys.getenv_opt key <> None then reject ("legacy semantic opt-in present: " ^ key)
    ) forbidden_legacy_keys;
    if Sys.getenv_opt "SORT4_R24_MUTABLE_CASE" = None then
      reject "closed mutable case selector missing";
    if Sys.getenv_opt "SORT4_R24_MUTABLE_REPO_ROOT" = None then
      reject "mutable repository root missing"

  let rec mut_ptr_element (ty : D.ty) =
    match ty.kind with
    | D.RawPtr {ty={kind=D.Param "Element"}; mutability=D.Mut} -> true
    | _ -> false

  let rec mut_ptr_mut_ptr_element (ty : D.ty) =
    match ty.kind with
    | D.RawPtr {ty=inner; mutability=D.Mut} -> mut_ptr_element inner
    | _ -> false

  let mut_maybeuninit_pointer (ty : D.ty) =
    match ty.kind with
    | D.Adt {id={name="std::mem::MaybeUninit"}; kind=D.UnionKind;
             substs=[{kind=D.Type inner}]} -> mut_ptr_element inner
    | _ -> false

  let local_decl body name =
    match List.filter (fun d ->
      LocalDeclIdRd.name_get (LocalDeclRd.id_get d) = name)
      (BodyRd.local_decls_get_list body) with
    | [decl] -> decl
    | _ -> reject ("exact mutable local " ^ name)

  let local_ty body name = D.decode_ty (LocalDeclRd.ty_get (local_decl body name))

  let fn_def call =
    match D.decode_operand (FnCallDataRd.func_get call) with
    | Constant {const=Val {ty={kind=FnDef {id={name}; substs;
                    late_bound_generic_param_count}}}} ->
        name, substs, late_bound_generic_param_count
    | _ -> reject "mutable call must use a typed constant FnDef"

  let fn_def_opt call =
    match D.decode_operand (FnCallDataRd.func_get call) with
    | Constant {const=Val {ty={kind=FnDef {id={name}; substs;
                    late_bound_generic_param_count}}}} ->
        Some (name, substs, late_bound_generic_param_count)
    | _ -> None

  let calls_named body name =
    List.filter_map (fun block ->
      match TerminatorKindRd.get
        (TerminatorRd.kind_get (BasicBlockRd.terminator_get block)) with
      | TerminatorKindRd.Call call ->
          (match fn_def_opt call with
           | Some (callee,_,_) when callee = name -> Some call
           | _ -> None)
      | _ -> None) (BodyRd.basic_blocks_get_list body)

  let target_id option =
    match OptionRd.get option with
    | OptionRd.Something pointer ->
        Stdint.Uint32.to_int (BasicBlockIdRd.index_get (VfMirRd.of_pointer pointer))
    | OptionRd.Nothing -> reject "mutable call missing normal successor"

  let cleanup_id call =
    match UnwindActionRd.get (FnCallDataRd.unwind_action_get call) with
    | UnwindActionRd.Cleanup id -> Stdint.Uint32.to_int (BasicBlockIdRd.index_get id)
    | _ -> reject "mutable call must retain Cleanup successor"

  let check_operand_local call name =
    match FnCallDataRd.args_get_list call with
    | [operand] ->
        (match OperandRd.get operand with
         | OperandRd.Move place when
             LocalDeclIdRd.name_get (PlaceRd.local_get place) = name &&
             PlaceRd.projection_get_list place = [] &&
             PlaceRd.local_is_mutable_get place -> ()
         | _ -> reject ("mutable call operand Move(" ^ name ^ ")"))
    | _ -> reject "mutable unary call arity"

  let check_destination call name =
    let place = FnCallDataRd.destination_get call in
    if LocalDeclIdRd.name_get (PlaceRd.local_get place) <> name ||
       PlaceRd.projection_get_list place <> [] then
      reject ("mutable call destination " ^ name)

  let one_call body name = match calls_named body name with
    | [call] -> call
    | _ -> reject ("exactly one mutable call to " ^ name)

  let check_outer_calls outer =
    let drop = one_call outer "std::ptr::mut_ptr::<impl *mut T>::drop_in_place" in
    let drop_name, drop_substs, drop_late = fn_def drop in
    if drop_name <> "std::ptr::mut_ptr::<impl *mut T>::drop_in_place" ||
       drop_late <> 0 ||
       not (match drop_substs with [{kind=D.Type t}] -> mut_ptr_element t | _ -> false) then
      reject "mutable pointer-drop FnDef/substitution";
    check_operand_local drop "_32";
    check_destination drop "_31";
    if target_id (FnCallDataRd.target_get drop) <> 16 || cleanup_id drop <> 28 then
      reject "mutable pointer-drop normal/Cleanup edge";
    let assume = one_call outer "std::mem::MaybeUninit::<T>::assume_init" in
    let assume_name, assume_substs, assume_late = fn_def assume in
    if assume_name <> "std::mem::MaybeUninit::<T>::assume_init" ||
       assume_late <> 0 ||
       not (match assume_substs with [{kind=D.Type t}] -> mut_ptr_element t | _ -> false) then
      reject "mutable assume_init FnDef/substitution";
    check_operand_local assume "_41";
    check_destination assume "_0";
    if target_id (FnCallDataRd.target_get assume) <> 25 || cleanup_id assume <> 28 then
      reject "mutable assume_init normal/Cleanup edge";
    drop, assume

  let check_a1_body body =
    let call = one_call body "std::mem::transmute_neo" in
    let _, substs, late = fn_def call in
    if late <> 0 || not (match substs with
      | [{kind=D.Type src}; {kind=D.Type dst}] ->
          mut_maybeuninit_pointer src && mut_ptr_element dst
      | _ -> false) then
      reject "mutable transmute_neo typed source/destination";
    (match FnCallDataRd.args_get_list call with
     | [operand] ->
         (match OperandRd.get operand with
          | OperandRd.Move place when PlaceRd.projection_get_list place = [] -> ()
          | _ -> reject "mutable transmute_neo must Move an unprojected local")
     | _ -> reject "mutable transmute_neo arity");
    ignore (target_id (FnCallDataRd.target_get call));
    call

  let check_select_calls outer =
    let calls = calls_named outer "std::intrinsics::select_unpredictable" in
    let ptrs, wrappers = List.fold_left (fun (ptrs, wrappers) call ->
      let _, substs, late = fn_def call in
      if late <> 0 then reject "mutable select intrinsic late-bound parameters";
      let kind = match substs with
        | [{kind=D.Type ty}] when mut_ptr_mut_ptr_element ty -> `Ptr
        | [{kind=D.Type ty}] when mut_maybeuninit_pointer ty -> `Wrapper
        | _ -> reject "mutable select intrinsic specialization" in
      if List.length (FnCallDataRd.args_get_list call) <> 3 then
        reject "mutable select intrinsic arity";
      ignore (target_id (FnCallDataRd.target_get call));
      match kind with `Ptr -> ptrs + 1, wrappers | `Wrapper -> ptrs, wrappers + 1
    ) (0,0) calls in
    if ptrs <> 2 || wrappers <> 1 then
      reject "mutable intrinsic call inventory (expected 2 pointer, 1 wrapper)";
    ptrs, wrappers

  let body_hash body =
    sort4_actual_owner_sha256
      (Marshal.to_string (D.decode_body body) [Marshal.No_sharing])

  let unit_hash vf_mir =
    sort4_actual_owner_sha256
      (Marshal.to_string (D.decode_vf_mir vf_mir) [Marshal.No_sharing])

  let source_path outer =
    match translate_span_data (BodyRd.fn_sig_span_get outer) with
    | Error _ -> reject "mutable source span decode"
    | Ok (Ast.Lexed (((path,_,_), (last,_,_))))
        when path = last && Filename.check_suffix path "verified/lib.rs" -> path
    | Ok _ -> reject "mutable source signature path"

  let check_source root selected source_path =
    let _, expected, _, _, _ = case_row selected in
    if sort4_actual_owner_sha256 (Sort4MaybeUninit.read_file source_path) <> expected then
      reject "exact mutable verified source SHA256";
    let original = Filename.concat
      (Filename.dirname (Filename.dirname source_path)) "original/lib.rs" in
    if sort4_actual_owner_sha256 (Sort4MaybeUninit.read_file original) <>
         "3bf0bf792c8135bf964f19b3aaadef38b8ca5ee9ec95107029ad99d28a807aaa" then
      reject "exact mutable original source SHA256";
    if not (Filename.is_relative root = false) || not (Sys.file_exists root) then
      reject "mutable std repository root is not absolute/existing"

  let certify vf_mir root =
    active := false;
    case := None;
    pointer_drop_redirects := 0;
    assume_init_redirects := 0;
    select_ptr_calls := 0;
    select_wrapper_calls := 0;
    forget_redirects := 0;
    reject_ambient_legacy ();
    Array.iter (fun entry ->
      let key = match String.index_opt entry '=' with
        | Some i -> String.sub entry 0 i | None -> entry in
      if String.starts_with ~prefix:"SORT4_" key &&
         not (List.mem key ["SORT4_R24_MUTABLE_CASE";
           "SORT4_R24_MUTABLE_REPO_ROOT"; "SORT4_R24_SESSION_PHASE_ID";
           "SORT4_R20_CALLEE_PHASE_ID"; "SORT4_SELECT_PROFILE"]) then
        reject ("ambient SORT4 selector: " ^ key)) (Unix.environment ());
    if Sys.getenv_opt "SMALLSORT_EXECUTION_PROVIDER" <> Some "cloud-build" ||
       Sys.getenv_opt "GITHUB_ACTIONS" <> None ||
       Args.ignore_unwind_paths || Args.skip_specless_fns then
      reject "Cloud exact full-body normal/unwind proof required";
    if not (exact_env "SORT4_R24_SESSION_PHASE_ID"
          "SORT4-ACTUAL-SELECT-2026-10-24-R24") ||
       not (exact_env "SORT4_R20_CALLEE_PHASE_ID"
          "SORT4-ACTUAL-SELECT-2026-10-23-R21") ||
       not (exact_env "SORT4_SELECT_PROFILE" "experimental-s6-26.10-v1") ||
       TranslatorArgs.ignore_unwind_paths then
      reject "exact R24/R21 profile and unwind-preserving route required";
    let selected = match Sys.getenv_opt "SORT4_R24_MUTABLE_CASE" with
      | Some value when List.mem value variants -> value
      | _ -> reject "mutable case selector must be one closed enum value" in
    let selected_root = match Sys.getenv_opt "SORT4_R24_MUTABLE_REPO_ROOT" with
      | Some path when not (Filename.is_relative path) &&
                       path = root && Sys.file_exists path && Sys.is_directory path -> path
      | _ -> reject "absolute mutable repository root required" in
    let private_gate = derived_legacy_env in
    if private_gate "SORT4_ACTUAL_OWNER_REPO_ROOT" selected selected_root <> Some selected_root ||
       private_gate "SORT4_ACTUAL_OWNER_ADMISSION" selected selected_root <> Some "1" ||
       private_gate "SORT4_ACTUAL_OWNER_NINE_ADMISSION" selected selected_root <> Some "1" ||
       private_gate "SORT4_ACTUAL_NESTED_H2_REPO_ROOT" selected selected_root <> Some selected_root ||
       private_gate "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT" selected selected_root <> Some selected_root ||
       private_gate "SORT4_A1_NINE_REPO_ROOT" selected selected_root <> Some selected_root ||
       private_gate "SORT4_R20_FINAL_SELECT_REPAIR" selected selected_root <> Some "1" ||
       private_gate "SORT4_R21_FRACTIONAL_FORGET" selected selected_root <> Some "1" ||
       private_gate "SORT4_R21_FRACTIONAL_VARIANT" selected selected_root <> Some selected then
      reject "closed route private legacy-derived certificate configuration";
    let bodies = VfMirRd.VfMir.bodies_get_list vf_mir in
    let expected_names = [
      "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new";
      "sort4_checked_as_mut_ptr"; "sort4_checked_pointer_drop";
      "sort4_checked_generic_drop"; "checked_transmute_neo_pointer";
      "checked_assume_init_pointer"; "checked_forget_owned";
      "select_unpredictable";
      "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop"
    ] in
    if List.map (fun body ->
         TrName.translate_def_path (BodyRd.def_path_get body)) bodies <> expected_names then
      reject "exact mutable nine-body DefPath/order";
    let variant, expected_source, expected_unit, expected_body6, expected_body7 =
      case_row selected in
    let _ = variant in
    check_source root selected (source_path (List.nth bodies 7));
    if unit_hash vf_mir <> expected_unit then
      reject "complete eager mutable decoded-unit SHA256";
    List.iteri (fun index body ->
      let expected = match List.assoc_opt index fixed_body_hashes with
        | Some digest -> digest
        | None when index = 6 -> expected_body6
        | None when index = 7 -> expected_body7
        | None -> reject "body index outside exact mutable inventory" in
      if body_hash body <> expected then
        reject ("complete eager mutable decoded body SHA256 at index " ^ string_of_int index)
    ) bodies;
    let outer = List.nth bodies 7 in
    if not (mut_ptr_mut_ptr_element (local_ty outer "_32")) ||
       not (mut_maybeuninit_pointer (local_ty outer "_41")) then
      reject "mutable outer typed locals _32/_41";
    ignore (check_outer_calls outer);
    ignore (check_select_calls outer);
    ignore (check_a1_body (List.nth bodies 5));
    (* Only now expose active state to the translation hook. *)
    case := Some selected;
    active := true


end
'''


def render() -> str:
    capture, matrix = load_pins()
    fixed, per_case = rows(capture, matrix)
    return TEMPLATE.replace("__FIXED_ROWS__", fixed).replace(
        "__CASE_ROWS__", per_case
    )


# Deterministic duplication keeps every existing const predicate and certificate
# intact. Only the new family gets mutable pointer predicates and fresh pins.
def native_overlay() -> tuple[str,str]:
    import re, importlib.util, difflib
    capture,matrix=load_pins()
    base=FROZEN_TRANSLATOR.read_text();lines=base.splitlines(True)
    modules=['MaybeUninit','AsMutPtr','PointerDrop','G1Call','GenericGuard',
             'ActualNestedH2','ActualForgetOwn','SelectIntrinsic','A1Link','A1Nine',
             'R24CheckedPointerOutcomes']
    helper=''.join(lines[9706:12638]+lines[12661:13976])
    names=re.findall(r'^  let (\w+)\b',helper,re.M)
    fnmap={n:n+'_mut' for n in names}
    fnmap['expected_sort4_redirects']='expected_sort4_mut_redirects'
    fnmap['expected_sort4_as_mut_ptr_redirects']='expected_sort4_mut_as_mut_ptr_redirects'
    def convert(text):
        for name in modules:text=text.replace('Sort4'+name,'Sort4Mut'+name)
        for name in sorted(fnmap,key=len,reverse=True):text=re.sub(r'\b'+name+r'\b',fnmap[name],text)
        text=text.replace('Sys.getenv_opt','Sort4MutableProfile.getenv_opt')
        text=text.replace('*const Element','*mut Element').replace('mutability = D.Not','mutability = D.Mut').replace('mutability=D.Not','mutability=D.Mut')
        return '\n'.join(line.rstrip() for line in text.split('\n'))
    state=convert(''.join(lines[349:1131])); helper=convert(helper)
    # Replace the exact eight-row constant table, not loosely matching digests.
    a=state.index('    let fractional_rows = [');b=state.index('    let fractional_row variant =',a)
    tuples=[]
    for variant in VARIANTS:
        row=matrix['cases'][variant];sn=row['snapshots']
        vals=[variant,row['source']['verified_sha256'],sn['body-6']['sha256'],sn['body-7']['sha256'],sn['unit']['sha256']]
        tuples.append('      ('+', '.join(quoted(v) for v in vals)+')')
    state=state[:a]+'    let fractional_rows = [\n'+';\n'.join(tuples)+'\n    ]\n'+state[b:]
    oldhashes=re.findall(r'"([0-9a-f]{64})"',''.join(lines[12700:12711]))
    # Explicitly bind fixed body hashes from the old nine-body table.
    oldfixed=['8d95311e339f94caed26d93fd339e279e8b1df9a3b783f202e99359e60d101cc',
      '92bd8aea548575b4b5cd8bdb826f807937c219a6872bec2ade2bce3bf25fc562',
      '273813f669fe0e34b486287539580e3cb487185f0be3691a1151ebf227685182',
      'f21b9915065deb75ded03903fc1b2781b3a19ebbe1561d2a9ca692b31931f951',
      'ac51fb48e423d64c3f8a96054c166b959303617f4affbd6665e10fe75cf6d4ed',
      '1c8531225e562d2d6492e79e049101f5884c580762733080686737d1c3cd07f6',
      'e0508d6cfb436bc1bcd04737ad74e37b357d17e9ec3c2a226ee961f7036eae9a']
    for index,old in zip((*range(6),8),oldfixed):
        helper=helper.replace(old,capture['snapshots'][f'body-{index}']['sha256'])
    helper=helper.replace('466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5',capture['source']['original_sha256'])
    profile='''  module Sort4MutableProfile = struct
    let root : string option ref = ref None
    let selected : string option ref = ref None
    let case_name () = match !selected with Some s -> s | None -> failwith "mutable case missing"
    let getenv_opt key =
      match !root, !selected with
      | Some r, Some c -> (match key with
          | "SORT4_MAYBEUNINIT_REPO_ROOT" | "SORT4_SELECT_INTRINSIC_REPO_ROOT"
          | "SORT4_POINTER_DROP_REPO_ROOT" | "SORT4_ACTUAL_OWNER_REPO_ROOT"
          | "SORT4_ACTUAL_NESTED_H2_REPO_ROOT" | "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT"
          | "SORT4_A1_NINE_REPO_ROOT" -> Some r
          | "SORT4_ACTUAL_OWNER_ADMISSION" | "SORT4_ACTUAL_OWNER_NINE_ADMISSION"
          | "SORT4_R20_FINAL_SELECT_REPAIR" | "SORT4_R21_FRACTIONAL_FORGET"
          | "SORT4_R24_CHECKED_POINTER_OUTCOMES" -> Some "1"
          | "SORT4_R21_FRACTIONAL_VARIANT" -> Some c
          | "SORT4_R24_SESSION_PHASE_ID" | "SORT4_R20_CALLEE_PHASE_ID"
          | "SORT4_SELECT_PROFILE" -> Sys.getenv_opt key
          | _ -> None)
      | _ -> None
  end
'''
    # The worker fragment is an additive current-unit source/hash/type check.
    fragment=render()
    init='''
  let check_sort4_mutable_body_inventory bodies =
    if !Sort4MutCertificate.active then (
      let names=List.map (fun b -> TrName.translate_def_path (BodyRd.def_path_get b)) bodies in
      if List.length names <> 9 || List.length (List.sort_uniq String.compare names) <> 9 then
        Sort4MutCertificate.reject "all nine ordinary body proofs required");
    Ok ()

  let certify_sort4_mutable_bundle vf_mir =
    Sort4MutableProfile.root := None;
    Sort4MutableProfile.selected := None;
    Sort4MutCertificate.active := false;
    Sort4MutMaybeUninit.active := false; Sort4MutAsMutPtr.active := false;
    Sort4MutPointerDrop.active := false; Sort4MutGenericGuard.active := false;
    Sort4MutGenericGuard.template_active := false; Sort4MutG1Call.active := false;
    Sort4MutActualNestedH2.active := false; Sort4MutActualForgetOwn.active := false;
    Sort4MutA1Link.active := false; Sort4MutA1Nine.active := false;
    Sort4MutR24CheckedPointerOutcomes.active := false;
    Sort4MutSelectIntrinsic.active := false;
    Sort4MutSelectIntrinsic.actual_certified := false;
    Sort4MutSelectIntrinsic.actual_owner_admitted := false;
    Sort4MutSelectIntrinsic.actual_nine_admitted := false;
    Sort4MutSelectIntrinsic.actual_fractional_variant := None;
    match Sys.getenv_opt "SORT4_R24_MUTABLE_CASE", Sys.getenv_opt "SORT4_R24_MUTABLE_REPO_ROOT" with
    | None,None -> Ok ()
    | Some selected,Some root ->
      Sort4MutCertificate.certify vf_mir root;
      Sort4MutableProfile.root := Some root;
      Sort4MutableProfile.selected := Some selected;
      let* () = certify_sort4_maybeuninit_mut vf_mir root in
      let* () = certify_sort4_as_mut_ptr_mut vf_mir root in
      let* () = certify_sort4_select_intrinsic_mut vf_mir root in
      let* () = certify_sort4_actual_nested_h2_mut vf_mir root in
      let* () = certify_sort4_actual_forget_own_mut vf_mir root in
      let* () = certify_sort4_pointer_drop_mut vf_mir root in
      let* () = certify_sort4_a1_nine_mut vf_mir root in
      Sort4MutR24CheckedPointerOutcomes.admit ()
    | _ -> Sort4MutCertificate.reject "partial mutable case/root selector"
'''
    hook_path=HERE/'mutable-translation-hooks.py'
    spec=importlib.util.spec_from_file_location('r24_mut_hookgen',hook_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    translated=module.generate(base)
    early='  module CapnpAux = struct\n'
    assert translated.count(early)==1
    translated=translated.replace(early,profile+state+'\n'+early,1)
    late='  let translate_vf_mir (extern_specs : string list)\n'
    assert translated.count(late)==1
    translated=translated.replace(late,helper+'\n'+fragment+'\n'+init+'\n'+late,1)
    patch=''.join(difflib.unified_diff(base.splitlines(True),translated.splitlines(True),fromfile='a/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',tofile='b/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'))
    return translated,patch


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render()
    translated,patch=native_overlay()
    Path("/tmp/r24-translator-mut.ml").write_text(translated)
    (HERE/"mutable-certificates-r24.patch").write_text(patch)
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("generated mutable certificate fragment is stale")
        print(f"OK {sha(OUT)}")
    else:
        OUT.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {OUT} sha256={sha(OUT)}")


if __name__ == "__main__":
    main()
