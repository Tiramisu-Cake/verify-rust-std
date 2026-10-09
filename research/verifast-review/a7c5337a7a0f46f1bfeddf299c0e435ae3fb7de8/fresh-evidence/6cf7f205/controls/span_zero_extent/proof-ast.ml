[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(10,1-28,2)", Regular, [("T", (true))], Some (ConstructedTypeExpr (loc "verified/lib.rs(10,45)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(10,45)", StructType ("std_tuple_0_", []))])), "span_zero_extent", [(ConstTypeExpr (loc "verified/lib.rs(10,35-36)", PtrTypeExpr (loc "verified/lib.rs(10,35-36)", IdentTypeExpr (loc "verified/lib.rs(10,35-36)", None, "T"))), "p")], false, (None, None), Some ((Sep (loc "verified/lib.rs(11,26-29)", CallExpr (loc "verified/lib.rs(11,9-21)", "thread_token", [], [], [VarPat (loc "verified/lib.rs(11,23-24)", "t")], Static), Sep (loc "verified/lib.rs(11,49-52)", Operation (loc "verified/lib.rs(11,32-34)", Eq, [Var (loc "verified/lib.rs(11,30-31)", "t"); Var (loc "verified/lib.rs(11,35-48)", "currentThread")]), Sep (loc "verified/lib.rs(11,72-75)", CallExpr (loc "verified/lib.rs(11,69-70)", "type_interp", [IdentTypeExpr (loc "verified/lib.rs(11,67-68)", None, "T")], [], [], Static), Sep (loc "verified/lib.rs(12,35-38)", Operation (loc "verified/lib.rs(12,30-32)", Eq, [SizeofExpr (loc "verified/lib.rs(12,27-28)", TypeExpr (IdentTypeExpr (loc "verified/lib.rs(12,25-26)", None, "T"))); IntLit (loc "verified/lib.rs(12,33-34)", big_int_of_string "0", false, false, NoLSuffix)]), Sep (loc "verified/lib.rs(12,55-58)", Operation (loc "verified/lib.rs(12,50-52)", Neq, [CastExpr (loc "verified/lib.rs(12,41-43)", ManifestTypeExpr (loc "verified/lib.rs(12,44-49)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(12,39-40)", "p")); IntLit (loc "verified/lib.rs(12,53-54)", big_int_of_string "0", false, false, NoLSuffix)]), Sep (loc "verified/lib.rs(13,49-52)", Operation (loc "verified/lib.rs(13,44-46)", Eq, [
      Operation (loc "verified/lib.rs(13,16-17)", Mod, [CastExpr (loc "verified/lib.rs(13,7-9)", ManifestTypeExpr (loc "verified/lib.rs(13,10-15)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(13,5-6)", "p")); AlignofExpr (loc "verified/lib.rs(13,41-42)", IdentTypeExpr (loc "verified/lib.rs(13,39-40)", None, "T"))]);
      IntLit (loc "verified/lib.rs(13,47-48)", big_int_of_string "0", false, false, NoLSuffix)
    ]), Sep (loc "verified/lib.rs(14,71-74)", Operation (loc "verified/lib.rs(14,63-65)", Eq, [
      CallExpr (loc "verified/lib.rs(14,5-33)", "object_pointer_within_limits", [], [], [LitPat (Var (loc "verified/lib.rs(14,34-35)", "p")); LitPat (SizeofExpr (loc "verified/lib.rs(14,59-60)", TypeExpr (IdentTypeExpr (loc "verified/lib.rs(14,57-58)", None, "T"))))], Static);
      True (loc "verified/lib.rs(14,66-70)")
    ]), Sep (loc "verified/lib.rs(15,15-18)", PointsTo (loc "verified/lib.rs(15,8-11)", Deref (loc "verified/lib.rs(15,5-6)", Var (loc "verified/lib.rs(15,6-7)", "p")), "RegularPointsTo", VarPat (loc "verified/lib.rs(15,13-14)", "v")), ExprCallExpr (loc "verified/lib.rs(15,26-27)", TypePredExpr (loc "verified/lib.rs(15,22-23)", IdentTypeExpr (loc "verified/lib.rs(15,20-21)", None, "T"), "own"), [LitPat (Var (loc "verified/lib.rs(15,27-28)", "t")); LitPat (Var (loc "verified/lib.rs(15,30-31)", "v"))]))))))))), ("outcome", SwitchExpr (loc "verified/lib.rs(10,45-16,88)", Var (loc "verified/lib.rs(10,45-16,88)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(16,29-32)", "returning", ["result"], Sep (loc "verified/lib.rs(16,29-32)", CallExpr (loc "verified/lib.rs(16,13-25)", "thread_token", [], [], [LitPat (Var (loc "verified/lib.rs(16,26-27)", "t"))], Static), Sep (loc "verified/lib.rs(16,52-55)", CallExpr (loc "verified/lib.rs(16,49-50)", "type_interp", [IdentTypeExpr (loc "verified/lib.rs(16,47-48)", None, "T")], [], [], Static), Sep (loc "verified/lib.rs(16,65-68)", PointsTo (loc "verified/lib.rs(16,59-62)", Deref (loc "verified/lib.rs(16,56-57)", Var (loc "verified/lib.rs(16,57-58)", "p")), "RegularPointsTo", LitPat (Var (loc "verified/lib.rs(16,63-64)", "v"))), ExprCallExpr (loc "verified/lib.rs(16,76-77)", TypePredExpr (loc "verified/lib.rs(16,72-73)", IdentTypeExpr (loc "verified/lib.rs(16,70-71)", None, "T"), "own"), [LitPat (Var (loc "verified/lib.rs(16,77-78)", "t")); LitPat (Var (loc "verified/lib.rs(16,80-81)", "v"))])))));
      SwitchExprClause (loc "verified/lib.rs(10,45-16,88)", "unwinding", [], EmpAsn (loc "verified/lib.rs(10,45-16,88)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(10,45)", StructType ("std_tuple_0_", []))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", IdentTypeExpr (loc "verified/lib.rs(17,9-12)", None, "T"))), "tmp", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (IdentTypeExpr (loc "verified/lib.rs(17,33-56)", None, "T")), "$_3", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (PtrTypeExpr (loc "verified/lib.rs(17,52-53)", IdentTypeExpr (loc "verified/lib.rs(17,52-53)", None, "T"))), "$_4", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (PtrTypeExpr (loc "verified/lib.rs(17,52-53)", IdentTypeExpr (loc "verified/lib.rs(17,52-53)", None, "T"))), "$_5", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(18,5-36)", StructType ("std_tuple_0_", [])))), "$_6", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(19,5-36)", StructType ("std_tuple_0_", [])))), "$_7", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(20,5-36)", StructType ("std_tuple_0_", [])))), "$_8", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(21,5-36)", StructType ("std_tuple_0_", [])))), "$_9", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", PtrTypeExpr (loc "verified/lib.rs(22,9-10)", IdentTypeExpr (loc "verified/lib.rs(22,9-10)", None, "T")))), "q", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (PtrTypeExpr (loc "verified/lib.rs(22,13-30)", IdentTypeExpr (loc "verified/lib.rs(22,13-30)", None, "T"))), "$_11", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", RustRefTypeExpr (loc "verified/lib.rs(22,13-18)", InferredTypeExpr (loc "verified/lib.rs(22,13-18)"), Shared, IdentTypeExpr (loc "verified/lib.rs(22,13-18)", None, "T")))), "$_12", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", RustRefTypeExpr (loc "verified/lib.rs(22,14-18)", InferredTypeExpr (loc "verified/lib.rs(22,14-18)"), Shared, IdentTypeExpr (loc "verified/lib.rs(22,14-18)", None, "T")))), "$_13", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (RustRefTypeExpr (loc "verified/lib.rs(22,15-18)", InferredTypeExpr (loc "verified/lib.rs(22,15-18)"), Shared, IdentTypeExpr (loc "verified/lib.rs(22,15-18)", None, "T"))), "$_14", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(23,5-36)", StructType ("std_tuple_0_", [])))), "$_15", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(24,5-50)", StructType ("std_tuple_0_", [])))), "$_16", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(24,14-47)", StructType ("std_tuple_0_", [])))), "$_17", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (PtrTypeExpr (loc "verified/lib.rs(24,39-40)", IdentTypeExpr (loc "verified/lib.rs(24,39-40)", None, "T"))), "$_18", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (PtrTypeExpr (loc "verified/lib.rs(24,42-43)", IdentTypeExpr (loc "verified/lib.rs(24,42-43)", None, "T"))), "$_19", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(25,5-36)", StructType ("std_tuple_0_", [])))), "$_20", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(26,5-36)", StructType ("std_tuple_0_", [])))), "$_21", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-28,2)", [(loc "verified/lib.rs(10,1-28,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-28,2)", ManifestTypeExpr (loc "verified/lib.rs(27,5-36)", StructType ("std_tuple_0_", [])))), "$_22", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(17,9-12)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(17,9-12)", loc "verified/lib.rs(17,9-12)", "_2", "tmp");
      RustStorageLiveStmt (loc "verified/lib.rs(17,33-56)", loc "verified/lib.rs(17,33-56)", "_3", "$_3");
      RustStorageLiveStmt (loc "verified/lib.rs(17,52-53)", loc "verified/lib.rs(17,52-53)", "_4", "$_4");
      RustStorageLiveStmt (loc "verified/lib.rs(17,52-53)", loc "verified/lib.rs(17,52-53)", "_5", "$_5");
      ExprStmt (AssignExpr (loc "verified/lib.rs(17,52-53)", Var (loc "verified/lib.rs(17,52-53)", "$_5"), Mutation, Var (loc "verified/lib.rs(17,52-53)", "p")));
      ExprStmt (AssignExpr (loc "verified/lib.rs(17,52-53)", Var (loc "verified/lib.rs(17,52-53)", "$_4"), Mutation, CastExpr (loc "verified/lib.rs(17,52-53)", PtrTypeExpr (loc "verified/lib.rs(17,52-53)", IdentTypeExpr (loc "verified/lib.rs(17,52-53)", None, "T")), Var (loc "verified/lib.rs(17,52-53)", "$_5"))));
      RustStorageDeadStmt (loc "verified/lib.rs(17,52-53)", loc "verified/lib.rs(17,52-53)", "_5", "$_5");
      ExprStmt (AssignExpr (loc "verified/lib.rs(17,42-54)", Var (loc "verified/lib.rs(17,42-54)", "$_3"), Mutation, Deref (loc "verified/lib.rs(17,42-54)", Var (loc "verified/lib.rs(17,42-54)", "$_4"))));
      RustStorageDeadStmt (loc "verified/lib.rs(17,53-54)", loc "verified/lib.rs(17,53-54)", "_4", "$_4");
      ExprStmt (AssignExpr (loc "verified/lib.rs(17,15-57)", Var (loc "verified/lib.rs(17,15-57)", "tmp"), Initialization, Var (loc "verified/lib.rs(17,15-57)", "$_3")));
      GotoStmt (loc "verified/lib.rs(17,15-57)", "2");
      LabelStmt (loc "verified/lib.rs(10,1-28,2)", "13");
      ReturnStmt (loc "verified/lib.rs(10,1-28,2)", Some (CallExpr (loc "verified/lib.rs(10,1-28,2)", "unwinding", [], [], [], Static)));
      LabelStmt (loc "verified/lib.rs(17,56-57)", "2");
      RustStorageDeadStmt (loc "verified/lib.rs(17,56-57)", loc "verified/lib.rs(17,56-57)", "_3", "$_3");
      RustStorageLiveStmt (loc "verified/lib.rs(18,5-36)", loc "verified/lib.rs(18,5-36)", "_6", "$_6");
      PureStmt (loc "verified/lib.rs(18,5-19,1)", DeclStmt (loc "verified/lib.rs(18,9-12)", [(loc "verified/lib.rs(18,13-14)", None, "k", Some (CallExpr (loc "verified/lib.rs(18,17-31)", "begin_lifetime", [], [], [], Static)), (ref (false), ref (None)))]));
      RustStorageDeadStmt (loc "verified/lib.rs(18,36-37)", loc "verified/lib.rs(18,36-37)", "_6", "$_6");
      RustStorageLiveStmt (loc "verified/lib.rs(19,5-36)", loc "verified/lib.rs(19,5-36)", "_7", "$_7");
      PureStmt (loc "verified/lib.rs(19,5-20,1)", DeclStmt (loc "verified/lib.rs(19,9-12)", [
        (loc "verified/lib.rs(19,13-21)", None, "held_ref", Some (CallExpr (loc "verified/lib.rs(19,24-37)", "precreate_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(19,38-39)", Var (loc "verified/lib.rs(19,39-42)", "tmp")))], Static)), (ref (false), ref (None)))
      ]));
      RustStorageDeadStmt (loc "verified/lib.rs(19,36-37)", loc "verified/lib.rs(19,36-37)", "_7", "$_7");
      RustStorageLiveStmt (loc "verified/lib.rs(20,5-36)", loc "verified/lib.rs(20,5-36)", "_8", "$_8");
      PureStmt (loc "verified/lib.rs(20,5-21,1)", MergeFractionsStmt (loc "verified/lib.rs(20,9-24)", CallExpr (loc "verified/lib.rs(20,25-39)", "lifetime_token", [], [], [LitPat (Var (loc "verified/lib.rs(20,40-41)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(20,36-37)", loc "verified/lib.rs(20,36-37)", "_8", "$_8");
      RustStorageLiveStmt (loc "verified/lib.rs(21,5-36)", loc "verified/lib.rs(21,5-36)", "_9", "$_9");
      PureStmt (loc "verified/lib.rs(21,5-22,1)", ExprStmt (CallExpr (loc "verified/lib.rs(21,9-26)", "init_ref_readonly", [], [], [
        LitPat (Var (loc "verified/lib.rs(21,27-35)", "held_ref"));
        LitPat (Operation (loc "verified/lib.rs(21,38-39)", Div, [IntLit (loc "verified/lib.rs(21,37-38)", big_int_of_string "1", true, false, NoLSuffix); IntLit (loc "verified/lib.rs(21,39-40)", big_int_of_string "2", true, false, NoLSuffix)]))
      ], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(21,36-37)", loc "verified/lib.rs(21,36-37)", "_9", "$_9");
      RustStorageLiveStmt (loc "verified/lib.rs(22,9-10)", loc "verified/lib.rs(22,9-10)", "_10", "q");
      RustStorageLiveStmt (loc "verified/lib.rs(22,13-30)", loc "verified/lib.rs(22,13-30)", "_11", "$_11");
      RustStorageLiveStmt (loc "verified/lib.rs(22,13-18)", loc "verified/lib.rs(22,13-18)", "_12", "$_12");
      RustStorageLiveStmt (loc "verified/lib.rs(22,14-18)", loc "verified/lib.rs(22,14-18)", "_13", "$_13");
      RustStorageLiveStmt (loc "verified/lib.rs(22,15-18)", loc "verified/lib.rs(22,15-18)", "_14", "$_14");
      ExprStmt (AssignExpr (loc "verified/lib.rs(22,15-18)", Var (loc "verified/lib.rs(22,15-18)", "$_14"), Mutation, CallExpr (loc "verified/lib.rs(22,15-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(22,15-18)", "create_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(22,15-18)", Var (loc "verified/lib.rs(22,15-18)", "tmp")))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(22,14-18)", Var (loc "verified/lib.rs(22,14-18)", "$_13"), Initialization, Var (loc "verified/lib.rs(22,14-18)", "$_14")));
      RustStorageDeadStmt (loc "verified/lib.rs(22,17-18)", loc "verified/lib.rs(22,17-18)", "_14", "$_14");
      ExprStmt (AssignExpr (loc "verified/lib.rs(22,13-18)", Var (loc "verified/lib.rs(22,13-18)", "$_12"), Initialization, CallExpr (loc "verified/lib.rs(22,13-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(22,13-18)", "reborrow_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(22,13-18)", Deref (loc "verified/lib.rs(22,13-18)", Var (loc "verified/lib.rs(22,13-18)", "$_13"))))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(22,13-18)", Var (loc "verified/lib.rs(22,13-18)", "$_11"), Mutation, AddressOf (loc "verified/lib.rs(22,13-18)", Deref (loc "verified/lib.rs(22,13-18)", Var (loc "verified/lib.rs(22,13-18)", "$_12")))));
      ExprStmt (AssignExpr (loc "verified/lib.rs(22,13-30)", Var (loc "verified/lib.rs(22,13-30)", "q"), Initialization, Var (loc "verified/lib.rs(22,13-30)", "$_11")));
      RustStorageDeadStmt (loc "verified/lib.rs(22,30-31)", loc "verified/lib.rs(22,30-31)", "_12", "$_12");
      RustStorageDeadStmt (loc "verified/lib.rs(22,30-31)", loc "verified/lib.rs(22,30-31)", "_11", "$_11");
      RustStorageLiveStmt (loc "verified/lib.rs(23,5-36)", loc "verified/lib.rs(23,5-36)", "_15", "$_15");
      PureStmt (loc "verified/lib.rs(23,5-91)", Assert (loc "verified/lib.rs(23,9-15)", Operation (loc "verified/lib.rs(23,27-29)", Neq, [CastExpr (loc "verified/lib.rs(23,18-20)", ManifestTypeExpr (loc "verified/lib.rs(23,21-26)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(23,16-17)", "q")); CastExpr (loc "verified/lib.rs(23,32-34)", ManifestTypeExpr (loc "verified/lib.rs(23,35-40)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(23,30-31)", "p"))])));
      RustStorageDeadStmt (loc "verified/lib.rs(23,36-37)", loc "verified/lib.rs(23,36-37)", "_15", "$_15");
      RustStorageLiveStmt (loc "verified/lib.rs(24,5-50)", loc "verified/lib.rs(24,5-50)", "_16", "$_16");
      RustStorageLiveStmt (loc "verified/lib.rs(24,14-47)", loc "verified/lib.rs(24,14-47)", "_17", "$_17");
      RustStorageLiveStmt (loc "verified/lib.rs(24,39-40)", loc "verified/lib.rs(24,39-40)", "_18", "$_18");
      ExprStmt (AssignExpr (loc "verified/lib.rs(24,39-40)", Var (loc "verified/lib.rs(24,39-40)", "$_18"), Mutation, Var (loc "verified/lib.rs(24,39-40)", "q")));
      RustStorageLiveStmt (loc "verified/lib.rs(24,42-43)", loc "verified/lib.rs(24,42-43)", "_19", "$_19");
      ExprStmt (AssignExpr (loc "verified/lib.rs(24,42-43)", Var (loc "verified/lib.rs(24,42-43)", "$_19"), Mutation, Var (loc "verified/lib.rs(24,42-43)", "p")));
      SwitchStmt (loc "verified/lib.rs(24,14-47)", CallExpr (loc "verified/lib.rs(24,14-47)", "std::ptr::merge_copy_nonoverlapping_one", [IdentTypeExpr (loc "verified/lib.rs(24,14-47)", None, "T")], [], [LitPat (Var (loc "verified/lib.rs(24,14-47)", "$_18")); LitPat (Var (loc "verified/lib.rs(24,14-47)", "$_19")); LitPat (CastExpr (loc "verified/lib.rs(24,45-46)", ManifestTypeExpr (loc "verified/lib.rs(24,45-46)", Int (Unsigned, PtrRank)), IntLit (loc "verified/lib.rs(24,45-46)", big_int_of_string "1", true, false, LLSuffix)))], Static), [
        SwitchStmtClause (loc "verified/lib.rs(24,14-47)", CallExpr (loc "verified/lib.rs(24,14-47)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(24,14-47)", "__result"))], Static), [ExprStmt (AssignExpr (loc "verified/lib.rs(24,14-47)", Var (loc "verified/lib.rs(24,14-47)", "$_17"), Initialization, Var (loc "verified/lib.rs(24,14-47)", "__result")))]);
        SwitchStmtClause (loc "verified/lib.rs(24,14-47)", CallExpr (loc "verified/lib.rs(24,14-47)", "unwinding", [], [], [], Static), [ReturnStmt (loc "verified/lib.rs(24,14-47)", Some (CallExpr (loc "verified/lib.rs(24,14-47)", "unwinding", [], [], [], Static)))])
      ]);
      RustStorageDeadStmt (loc "verified/lib.rs(24,46-47)", loc "verified/lib.rs(24,46-47)", "_19", "$_19");
      RustStorageDeadStmt (loc "verified/lib.rs(24,46-47)", loc "verified/lib.rs(24,46-47)", "_18", "$_18");
      RustStorageDeadStmt (loc "verified/lib.rs(24,47-48)", loc "verified/lib.rs(24,47-48)", "_17", "$_17");
      RustStorageDeadStmt (loc "verified/lib.rs(24,49-50)", loc "verified/lib.rs(24,49-50)", "_16", "$_16");
      RustStorageLiveStmt (loc "verified/lib.rs(25,5-36)", loc "verified/lib.rs(25,5-36)", "_20", "$_20");
      PureStmt (loc "verified/lib.rs(25,5-26,1)", ExprStmt (CallExpr (loc "verified/lib.rs(25,9-25)", "end_ref_readonly", [], [], [LitPat (Var (loc "verified/lib.rs(25,26-34)", "held_ref"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(25,36-37)", loc "verified/lib.rs(25,36-37)", "_20", "$_20");
      RustStorageLiveStmt (loc "verified/lib.rs(26,5-36)", loc "verified/lib.rs(26,5-36)", "_21", "$_21");
      PureStmt (loc "verified/lib.rs(26,5-27,1)", MergeFractionsStmt (loc "verified/lib.rs(26,9-24)", CallExpr (loc "verified/lib.rs(26,39-40)", "points_to", [IdentTypeExpr (loc "verified/lib.rs(26,37-38)", None, "T")], [], [LitPat (AddressOf (loc "verified/lib.rs(26,40-41)", Var (loc "verified/lib.rs(26,41-44)", "tmp"))); DummyPat], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(26,36-37)", loc "verified/lib.rs(26,36-37)", "_21", "$_21");
      RustStorageLiveStmt (loc "verified/lib.rs(27,5-36)", loc "verified/lib.rs(27,5-36)", "_22", "$_22");
      PureStmt (loc "verified/lib.rs(27,5-28,1)", ExprStmt (CallExpr (loc "verified/lib.rs(27,9-21)", "end_lifetime", [], [], [LitPat (Var (loc "verified/lib.rs(27,22-23)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(27,36-37)", loc "verified/lib.rs(27,36-37)", "_22", "$_22");
      RustStorageDeadStmt (loc "verified/lib.rs(28,1-2)", loc "verified/lib.rs(28,1-2)", "_13", "$_13");
      RustStorageDeadStmt (loc "verified/lib.rs(28,1-2)", loc "verified/lib.rs(28,1-2)", "_10", "q");
      RustStorageDeadStmt (loc "verified/lib.rs(28,1-2)", loc "verified/lib.rs(28,1-2)", "_2", "tmp");
      ReturnStmt (loc "verified/lib.rs(28,2)", Some (CallExpr (loc "verified/lib.rs(28,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(28,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(28,1-2)")), false, [])
  ])
]