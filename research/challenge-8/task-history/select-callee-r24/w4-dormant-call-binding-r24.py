"""Authoring snippets only. No source preparation or tool execution."""
MODULE = r'''  (* Dormant R24 call consumption. No code in this candidate activates Caller
     or supplies a checked contract. Activation needs its own reviewed route. *)
  module Sort4R24W4Calls = struct
    let header_consumed = ref false
    let actual_contract : string option ref = ref None
    let header_path : string option ref = ref None
    let redirected : string list list ref = ref []
    let callee_name = "r24_select::select_unpredictable_const"
    let reject why = Sort4R24W4Caller.reject ("ordinary call binding: " ^ why)
    let const_t (ty : D.ty) = match ty.kind with
      | D.RawPtr {ty={kind=D.Param "T"}; mutability=D.Not} -> true
      | _ -> false
    let expected_sites = [
      (["_184";"_185";"_186"], "_183");
      (["_188";"_189";"_190"], "_187");
      (["_195";"_196";"_197"], "_194");
      (["_192";"_193";"_194"], "_191");
      (["_202";"_203";"_204"], "_201");
      (["_199";"_200";"_201"], "_198");
      (["_243";"_244";"_245"], "_242");
      (["_247";"_248";"_249"], "_246")
    ]
    let operand_local operand =
      let place = match OperandRd.get operand with
        | OperandRd.Move p | OperandRd.Copy p -> p
        | _ -> reject "expected compiler-origin copy/move operand" in
      if PlaceRd.projection_get_list place <> [] then
        reject "projected operand";
      LocalDeclIdRd.name_get (PlaceRd.local_get place)
    let local_ty locals id = match List.assoc_opt id locals with
      | Some ty -> ty | None -> reject "missing typed local"
    let check_args locals operands =
      let ids = List.map operand_local operands in
      (match ids with
       | [condition; left; right] ->
           (match (local_ty locals condition).kind with
            | D.Bool -> () | _ -> reject "condition is not bool");
           if not (const_t (local_ty locals left) &&
                   const_t (local_ty locals right)) then
             reject "operand is not exact constpointer T"
       | _ -> reject "expected exactly three operands");
      if not (List.mem_assoc ids expected_sites) then
        reject "unrecognized exact operand tuple";
      ids
    let consume_headers headers =
      if !Sort4R24W4Caller.active then (
        if !header_consumed then reject "header consumed more than once";
        let expected, path = match !actual_contract, !header_path with
          | Some spec, Some path -> spec, path
          | _ -> reject "no sameversion checked contract/header certificate" in
        let named_headers = List.filter (fun (_, (_, _, p), _, _) -> p = path) headers in
        let packages = match named_headers with
          | [(_, _, _, packages)] -> packages
          | _ -> reject "expected unique actual returned header" in
        let nonempty = List.filter_map (function
          | Ast.PackageDecl (_, _, _, []) -> None
          | Ast.PackageDecl (_, pn, imports, ds) -> Some (pn, imports, ds)) packages in
        let imported = match nonempty with
          | [("r24_select", [], [Ast.Func (_, Ast.Regular,
              ["Element", {Ast.sized=true}],
              Some (Ast.ConstructedTypeExpr (_, "fn_outcome",
                [Ast.PtrTypeExpr (_, Ast.IdentTypeExpr (_, None, "Element"))])),
              "select_unpredictable_const",
              [(Ast.ManifestTypeExpr (_, Ast.Bool), "condition");
               (Ast.PtrTypeExpr (_, Ast.IdentTypeExpr (_, None, "Element")), "true_val");
               (Ast.PtrTypeExpr (_, Ast.IdentTypeExpr (_, None, "Element")), "false_val")],
              false, (None, None), Some spec, false, None, false, [])])] ->
                Ocaml_expr_formatter.string_of_ocaml_expr true
                  (Ocaml_expr_of_ast.of_spec spec)
          | _ -> reject "actual returned header declaration shape" in
        let package_count = List.fold_left (fun n (_, _, _, packages) ->
          n + List.length (List.filter (function
            | Ast.PackageDecl (_, "r24_select", _, ds) when ds <> [] -> true
            | _ -> false) packages)) 0 headers in
        if package_count <> 1 || imported <> expected then
          reject "duplicate namespace or actual/consumed contract mismatch";
        header_consumed := true
      )
    let finish () =
      if !Sort4R24W4Caller.active then (
        if not !header_consumed ||
           List.sort compare !redirected <>
             List.sort compare (List.map fst expected_sites) then
          reject "expected exactly eight unique consumed ordinary calls"
      )
  end

'''
PROJECT = r'''          let fn_name, substs_cpn =
            if !Sort4R24W4Caller.active &&
               fn_def_ty_cpn.id.name = "std::hint::select_unpredictable" then (
              if State.body_name <> "sort4_stable" ||
                 fn_def_ty_cpn.late_bound_generic_param_count <> 0 ||
                 not !Sort4R24W4Calls.header_consumed ||
                 OptionRd.get ghost_generic_arg_list_opt_cpn <> OptionRd.Nothing then
                Sort4R24W4Calls.reject "caller/latebound/header/ghost-arguments";
              (match substs_cpn with
               | [{kind=D.Type ty}] when Sort4R24W4Calls.const_t ty -> ()
               | _ -> Sort4R24W4Calls.reject "singleton constpointer substitution");
              let ids = Sort4R24W4Calls.check_args Args.local_decl_types args_cpn in
              if List.mem ids !Sort4R24W4Calls.redirected then
                Sort4R24W4Calls.reject "duplicate ordinary call site";
              Sort4R24W4Calls.redirected := ids :: !Sort4R24W4Calls.redirected;
              (Sort4R24W4Calls.callee_name, [{D.kind=D.Type {D.kind=D.Param "T"}}])
            ) else
              Args.body_tr_defs_ctx.fn_specializer fn_name substs_cpn
          in
'''
EDGE = r'''      let () =
        if !Sort4R24W4Caller.active then
          match D.decode_operand func_cpn with
          | D.Constant {const=D.Val {ty={kind=D.FnDef {id={name="std::hint::select_unpredictable"}; _}}}} ->
              let ids = Sort4R24W4Calls.check_args Args.local_decl_types args_cpn in
              let place = destination_get fn_call_data_cpn in
              let dest = LocalDeclIdRd.name_get (PlaceRd.local_get place) in
              if PlaceRd.projection_get_list place <> [] ||
                 not (Sort4R24W4Calls.const_t
                   (Sort4R24W4Calls.local_ty Args.local_decl_types dest)) ||
                 List.assoc ids Sort4R24W4Calls.expected_sites <> dest then
                Sort4R24W4Calls.reject "destination does not match typed site";
              (match OptionRd.get (target_get fn_call_data_cpn), fn_call_rexpr with
               | OptionRd.Something _, FnCallOutcome
                   (Ast.CallExpr (_, name,
                     [Ast.IdentTypeExpr (_, None, "T")], [],
                     [Ast.LitPat _;Ast.LitPat _;Ast.LitPat _], Ast.Static))
                     when name = Sort4R24W4Calls.callee_name &&
                          not TranslatorArgs.ignore_unwind_paths -> ()
               | _ -> Sort4R24W4Calls.reject "ordinary outcome/normal target/unwind policy")
              (* Do not change target, destination, arguments or unwind_action.
                 Existing translation below consumes the original MIR edges. *)
          | _ -> ()
      in
'''
def once(text,old,new):
    assert text.count(old)==1,(old[:100],text.count(old))
    return text.replace(old,new)
def generate(text):
    assert 'module Sort4R24W4Caller = struct' in text
    text=once(text,'  module TrBody (Args : sig\n',MODULE+'  module TrBody (Args : sig\n')
    text=once(text,'          let fn_name, substs_cpn =\n            Args.body_tr_defs_ctx.fn_specializer fn_name substs_cpn\n          in\n',PROJECT)
    text=once(text,'      let checked_g1_no_unwind =\n',EDGE+'      let checked_g1_no_unwind =\n')
    text=once(text,'      let fn_specialization_decls = List.flatten fn_specialization_decls in\n','      let fn_specialization_decls = List.flatten fn_specialization_decls in\n      let () = Sort4R24W4Calls.consume_headers headers in\n')
    text=once(text,'      (* `vfide` relies on the similarity of the order of function declarations\n','      let () = Sort4R24W4Calls.finish () in\n      (* `vfide` relies on the similarity of the order of function declarations\n')
    return text
