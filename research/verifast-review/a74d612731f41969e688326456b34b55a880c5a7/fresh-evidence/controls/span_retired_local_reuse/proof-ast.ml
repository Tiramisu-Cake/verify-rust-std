[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(10,1-36,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(10,45-48)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(10,45-48)", Int (Unsigned, FixedWidthRank (3)))])), "span_retired_local_reuse", [], false, (None, None), Some ((True (loc "verified/lib.rs(11,9-13)"), ("outcome", SwitchExpr (loc "verified/lib.rs(10,48-11,44)", Var (loc "verified/lib.rs(10,48-11,44)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(11,34-36)", "returning", ["result"], Operation (loc "verified/lib.rs(11,34-36)", Eq, [Var (loc "verified/lib.rs(11,27-33)", "result"); IntLit (loc "verified/lib.rs(11,37-38)", big_int_of_string "9", true, false, NoLSuffix)]));
      SwitchExprClause (loc "verified/lib.rs(10,48-11,44)", "unwinding", [], EmpAsn (loc "verified/lib.rs(10,48-11,44)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(10,45-48)", Int (Unsigned, FixedWidthRank (3)))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", PtrTypeExpr (loc "verified/lib.rs(12,9-14)", ManifestTypeExpr (loc "verified/lib.rs(12,9-14)", Int (Unsigned, FixedWidthRank (3)))))), "saved", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(13,13-17)", Int (Unsigned, FixedWidthRank (3))))), "tmp0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(16,9-40)", StructType ("std_tuple_0_", [])))), "$_3", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(17,9-40)", StructType ("std_tuple_0_", [])))), "$_4", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(18,9-40)", StructType ("std_tuple_0_", [])))), "$_5", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", PtrTypeExpr (loc "verified/lib.rs(19,13-15)", ManifestTypeExpr (loc "verified/lib.rs(19,13-15)", Int (Unsigned, FixedWidthRank (3)))))), "q0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", RustRefTypeExpr (loc "verified/lib.rs(19,18-24)", InferredTypeExpr (loc "verified/lib.rs(19,18-24)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,18-24)", Int (Unsigned, FixedWidthRank (3)))))), "$_7", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", RustRefTypeExpr (loc "verified/lib.rs(19,19-24)", InferredTypeExpr (loc "verified/lib.rs(19,19-24)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,19-24)", Int (Unsigned, FixedWidthRank (3)))))), "$_8", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (RustRefTypeExpr (loc "verified/lib.rs(19,20-24)", InferredTypeExpr (loc "verified/lib.rs(19,20-24)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,20-24)", Int (Unsigned, FixedWidthRank (3))))), "$_9", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(20,9-40)", StructType ("std_tuple_0_", [])))), "$_10", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(21,9-40)", StructType ("std_tuple_0_", [])))), "$_11", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(24,9-13)", Int (Unsigned, FixedWidthRank (3))))), "tmp1", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(25,5-36)", StructType ("std_tuple_0_", [])))), "$_13", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(26,5-36)", StructType ("std_tuple_0_", [])))), "$_14", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(27,5-36)", StructType ("std_tuple_0_", [])))), "$_15", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(28,5-36)", StructType ("std_tuple_0_", [])))), "$_16", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", PtrTypeExpr (loc "verified/lib.rs(29,9-13)", ManifestTypeExpr (loc "verified/lib.rs(29,9-13)", Int (Unsigned, FixedWidthRank (3)))))), "newq", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", RustRefTypeExpr (loc "verified/lib.rs(29,16-22)", InferredTypeExpr (loc "verified/lib.rs(29,16-22)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(29,16-22)", Int (Unsigned, FixedWidthRank (3)))))), "$_18", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", RustRefTypeExpr (loc "verified/lib.rs(29,17-22)", InferredTypeExpr (loc "verified/lib.rs(29,17-22)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(29,17-22)", Int (Unsigned, FixedWidthRank (3)))))), "$_19", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (RustRefTypeExpr (loc "verified/lib.rs(29,18-22)", InferredTypeExpr (loc "verified/lib.rs(29,18-22)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(29,18-22)", Int (Unsigned, FixedWidthRank (3))))), "$_20", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(30,5-36)", StructType ("std_tuple_0_", [])))), "$_21", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(31,9-15)", Int (Unsigned, FixedWidthRank (3))))), "result", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(32,5-36)", StructType ("std_tuple_0_", [])))), "$_23", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(33,5-36)", StructType ("std_tuple_0_", [])))), "$_24", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-36,2)", [(loc "verified/lib.rs(10,1-36,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-36,2)", ManifestTypeExpr (loc "verified/lib.rs(34,5-36)", StructType ("std_tuple_0_", [])))), "$_25", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(12,9-14)", "0");
      ExprStmt (CallExpr (loc "verified/lib.rs(12,9-14)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(12,9-14)", "saved"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(13,13-17)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(13,13-17)", "tmp0"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(13,20-44)", Var (loc "verified/lib.rs(13,20-44)", "tmp0"), Initialization, CastExpr (loc "verified/lib.rs(13,38-43)", ManifestTypeExpr (loc "verified/lib.rs(13,38-43)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(13,38-43)", big_int_of_string "7", true, false, LLSuffix))));
      ExprStmt (CallExpr (loc "verified/lib.rs(16,9-40)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(16,9-40)", "$_3"))], Static));
      PureStmt (loc "verified/lib.rs(16,9-17,1)", DeclStmt (loc "verified/lib.rs(16,13-16)", [(loc "verified/lib.rs(16,17-19)", None, "k0", Some (CallExpr (loc "verified/lib.rs(16,22-36)", "begin_lifetime", [], [], [], Static)), (ref (false), ref (None)))]));
      ExprStmt (CallExpr (loc "verified/lib.rs(16,40-41)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(16,40-41)", "$_3"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(17,9-40)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(17,9-40)", "$_4"))], Static));
      PureStmt (loc "verified/lib.rs(17,9-18,1)", DeclStmt (loc "verified/lib.rs(17,13-16)", [
        (loc "verified/lib.rs(17,17-21)", None, "ref0", Some (CallExpr (loc "verified/lib.rs(17,24-37)", "precreate_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(17,38-39)", Var (loc "verified/lib.rs(17,39-43)", "tmp0")))], Static)), (ref (false), ref (None)))
      ]));
      ExprStmt (CallExpr (loc "verified/lib.rs(17,40-41)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(17,40-41)", "$_4"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(18,9-40)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(18,9-40)", "$_5"))], Static));
      PureStmt (loc "verified/lib.rs(18,9-19,1)", ExprStmt (CallExpr (loc "verified/lib.rs(18,13-30)", "init_ref_readonly", [], [], [
        LitPat (Var (loc "verified/lib.rs(18,31-35)", "ref0"));
        LitPat (Operation (loc "verified/lib.rs(18,38-39)", Div, [IntLit (loc "verified/lib.rs(18,37-38)", big_int_of_string "1", true, false, NoLSuffix); IntLit (loc "verified/lib.rs(18,39-40)", big_int_of_string "2", true, false, NoLSuffix)]))
      ], Static)));
      ExprStmt (CallExpr (loc "verified/lib.rs(18,40-41)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(18,40-41)", "$_5"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(19,13-15)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(19,13-15)", "q0"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(19,18-24)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(19,18-24)", "$_7"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(19,19-24)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(19,19-24)", "$_8"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(19,20-24)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(19,20-24)", "$_9"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,20-24)", Var (loc "verified/lib.rs(19,20-24)", "$_9"), Mutation, CallExpr (loc "verified/lib.rs(19,20-24)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(19,20-24)", "create_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(19,20-24)", Var (loc "verified/lib.rs(19,20-24)", "tmp0")))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,19-24)", Var (loc "verified/lib.rs(19,19-24)", "$_8"), Initialization, Var (loc "verified/lib.rs(19,19-24)", "$_9")));
      ExprStmt (CallExpr (loc "verified/lib.rs(19,23-24)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(19,23-24)", "$_9"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,18-24)", Var (loc "verified/lib.rs(19,18-24)", "$_7"), Initialization, CallExpr (loc "verified/lib.rs(19,18-24)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(19,18-24)", "reborrow_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(19,18-24)", Deref (loc "verified/lib.rs(19,18-24)", Var (loc "verified/lib.rs(19,18-24)", "$_8"))))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,18-24)", Var (loc "verified/lib.rs(19,18-24)", "q0"), Initialization, AddressOf (loc "verified/lib.rs(19,18-24)", Deref (loc "verified/lib.rs(19,18-24)", Var (loc "verified/lib.rs(19,18-24)", "$_7")))));
      ExprStmt (CallExpr (loc "verified/lib.rs(19,38-39)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(19,38-39)", "$_7"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(20,9-40)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(20,9-40)", "$_10"))], Static));
      PureStmt (loc "verified/lib.rs(20,9-21,1)", ExprStmt (CallExpr (loc "verified/lib.rs(20,13-29)", "end_ref_readonly", [], [], [LitPat (Var (loc "verified/lib.rs(20,30-34)", "ref0"))], Static)));
      ExprStmt (CallExpr (loc "verified/lib.rs(20,40-41)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(20,40-41)", "$_10"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(21,9-40)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(21,9-40)", "$_11"))], Static));
      PureStmt (loc "verified/lib.rs(21,9-22,1)", ExprStmt (CallExpr (loc "verified/lib.rs(21,13-25)", "end_lifetime", [], [], [LitPat (Var (loc "verified/lib.rs(21,26-28)", "k0"))], Static)));
      ExprStmt (CallExpr (loc "verified/lib.rs(21,40-41)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(21,40-41)", "$_11"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(22,9-11)", Var (loc "verified/lib.rs(22,9-11)", "saved"), Initialization, Var (loc "verified/lib.rs(22,9-11)", "q0")));
      ExprStmt (CallExpr (loc "verified/lib.rs(23,5-6)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(23,5-6)", "$_8"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(23,5-6)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(23,5-6)", "q0"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(23,5-6)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(23,5-6)", "tmp0"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(24,9-13)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(24,9-13)", "tmp1"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(24,16-40)", Var (loc "verified/lib.rs(24,16-40)", "tmp1"), Initialization, CastExpr (loc "verified/lib.rs(24,34-39)", ManifestTypeExpr (loc "verified/lib.rs(24,34-39)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(24,34-39)", big_int_of_string "9", true, false, LLSuffix))));
      ExprStmt (CallExpr (loc "verified/lib.rs(25,5-36)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(25,5-36)", "$_13"))], Static));
      PureStmt (loc "verified/lib.rs(25,5-26,1)", DeclStmt (loc "verified/lib.rs(25,9-12)", [(loc "verified/lib.rs(25,13-15)", None, "k1", Some (CallExpr (loc "verified/lib.rs(25,18-32)", "begin_lifetime", [], [], [], Static)), (ref (false), ref (None)))]));
      ExprStmt (CallExpr (loc "verified/lib.rs(25,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(25,36-37)", "$_13"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(26,5-36)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(26,5-36)", "$_14"))], Static));
      PureStmt (loc "verified/lib.rs(26,5-27,1)", DeclStmt (loc "verified/lib.rs(26,9-12)", [
        (loc "verified/lib.rs(26,13-17)", None, "ref1", Some (CallExpr (loc "verified/lib.rs(26,20-33)", "precreate_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(26,34-35)", Var (loc "verified/lib.rs(26,35-39)", "tmp1")))], Static)), (ref (false), ref (None)))
      ]));
      ExprStmt (CallExpr (loc "verified/lib.rs(26,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(26,36-37)", "$_14"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(27,5-36)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(27,5-36)", "$_15"))], Static));
      PureStmt (loc "verified/lib.rs(27,5-28,1)", MergeFractionsStmt (loc "verified/lib.rs(27,9-24)", CallExpr (loc "verified/lib.rs(27,25-39)", "lifetime_token", [], [], [LitPat (Var (loc "verified/lib.rs(27,40-42)", "k1"))], Static)));
      ExprStmt (CallExpr (loc "verified/lib.rs(27,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(27,36-37)", "$_15"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(28,5-36)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(28,5-36)", "$_16"))], Static));
      PureStmt (loc "verified/lib.rs(28,5-29,1)", ExprStmt (CallExpr (loc "verified/lib.rs(28,9-26)", "init_ref_readonly", [], [], [
        LitPat (Var (loc "verified/lib.rs(28,27-31)", "ref1"));
        LitPat (Operation (loc "verified/lib.rs(28,34-35)", Div, [IntLit (loc "verified/lib.rs(28,33-34)", big_int_of_string "1", true, false, NoLSuffix); IntLit (loc "verified/lib.rs(28,35-36)", big_int_of_string "2", true, false, NoLSuffix)]))
      ], Static)));
      ExprStmt (CallExpr (loc "verified/lib.rs(28,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(28,36-37)", "$_16"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(29,9-13)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(29,9-13)", "newq"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(29,16-22)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(29,16-22)", "$_18"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(29,17-22)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(29,17-22)", "$_19"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(29,18-22)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(29,18-22)", "$_20"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(29,18-22)", Var (loc "verified/lib.rs(29,18-22)", "$_20"), Mutation, CallExpr (loc "verified/lib.rs(29,18-22)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(29,18-22)", "create_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(29,18-22)", Var (loc "verified/lib.rs(29,18-22)", "tmp1")))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(29,17-22)", Var (loc "verified/lib.rs(29,17-22)", "$_19"), Initialization, Var (loc "verified/lib.rs(29,17-22)", "$_20")));
      ExprStmt (CallExpr (loc "verified/lib.rs(29,21-22)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(29,21-22)", "$_20"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(29,16-22)", Var (loc "verified/lib.rs(29,16-22)", "$_18"), Initialization, CallExpr (loc "verified/lib.rs(29,16-22)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(29,16-22)", "reborrow_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(29,16-22)", Deref (loc "verified/lib.rs(29,16-22)", Var (loc "verified/lib.rs(29,16-22)", "$_19"))))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(29,16-22)", Var (loc "verified/lib.rs(29,16-22)", "newq"), Initialization, AddressOf (loc "verified/lib.rs(29,16-22)", Deref (loc "verified/lib.rs(29,16-22)", Var (loc "verified/lib.rs(29,16-22)", "$_18")))));
      ExprStmt (CallExpr (loc "verified/lib.rs(29,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(29,36-37)", "$_18"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(30,5-36)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(30,5-36)", "$_21"))], Static));
      PureStmt (loc "verified/lib.rs(30,5-103)", Assert (loc "verified/lib.rs(30,9-15)", Operation (loc "verified/lib.rs(30,30-32)", Neq, [CastExpr (loc "verified/lib.rs(30,21-23)", ManifestTypeExpr (loc "verified/lib.rs(30,24-29)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(30,16-20)", "newq")); CastExpr (loc "verified/lib.rs(30,39-41)", ManifestTypeExpr (loc "verified/lib.rs(30,42-47)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(30,33-38)", "saved"))])));
      ExprStmt (CallExpr (loc "verified/lib.rs(30,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(30,36-37)", "$_21"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(31,9-15)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(31,9-15)", "result"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(31,27-32)", Var (loc "verified/lib.rs(31,27-32)", "result"), Initialization, Deref (loc "verified/lib.rs(31,27-32)", Var (loc "verified/lib.rs(31,27-32)", "newq"))));
      ExprStmt (CallExpr (loc "verified/lib.rs(32,5-36)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(32,5-36)", "$_23"))], Static));
      PureStmt (loc "verified/lib.rs(32,5-33,1)", ExprStmt (CallExpr (loc "verified/lib.rs(32,9-25)", "end_ref_readonly", [], [], [LitPat (Var (loc "verified/lib.rs(32,26-30)", "ref1"))], Static)));
      ExprStmt (CallExpr (loc "verified/lib.rs(32,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(32,36-37)", "$_23"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(33,5-36)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(33,5-36)", "$_24"))], Static));
      PureStmt (loc "verified/lib.rs(33,5-34,1)", MergeFractionsStmt (loc "verified/lib.rs(33,9-24)", CallExpr (loc "verified/lib.rs(33,41-42)", "points_to", [ManifestTypeExpr (loc "verified/lib.rs(33,37-40)", Int (Unsigned, FixedWidthRank (3)))], [], [LitPat (AddressOf (loc "verified/lib.rs(33,42-43)", Var (loc "verified/lib.rs(33,43-47)", "tmp1"))); DummyPat], Static)));
      ExprStmt (CallExpr (loc "verified/lib.rs(33,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(33,36-37)", "$_24"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(34,5-36)", "vf__rust_storage_live", [], [], [LitPat (Var (loc "verified/lib.rs(34,5-36)", "$_25"))], Static));
      PureStmt (loc "verified/lib.rs(34,5-35,1)", ExprStmt (CallExpr (loc "verified/lib.rs(34,9-21)", "end_lifetime", [], [], [LitPat (Var (loc "verified/lib.rs(34,22-24)", "k1"))], Static)));
      ExprStmt (CallExpr (loc "verified/lib.rs(34,36-37)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(34,36-37)", "$_25"))], Static));
      ExprStmt (AssignExpr (loc "verified/lib.rs(35,5-11)", Var (loc "verified/lib.rs(35,5-11)", "$_0"), Mutation, Var (loc "verified/lib.rs(35,5-11)", "result")));
      ExprStmt (CallExpr (loc "verified/lib.rs(36,1-2)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(36,1-2)", "result"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(36,1-2)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(36,1-2)", "$_19"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(36,1-2)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(36,1-2)", "newq"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(36,1-2)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(36,1-2)", "tmp1"))], Static));
      ExprStmt (CallExpr (loc "verified/lib.rs(36,1-2)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(36,1-2)", "saved"))], Static));
      ReturnStmt (loc "verified/lib.rs(36,2)", Some (CallExpr (loc "verified/lib.rs(36,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(36,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(36,1-2)")), false, [])
  ])
]