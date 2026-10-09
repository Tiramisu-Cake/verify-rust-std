[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(10,1-13,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(10,38)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(10,38)", StructType ("std_tuple_0_", []))])), "origin_local_may_panic", [(ConstTypeExpr (loc "verified/lib.rs(10,27-31)", ManifestTypeExpr (loc "verified/lib.rs(10,27-31)", Bool)), "flag")], false, (None, None), Some ((Sep (loc "verified/lib.rs(10,1-38)", Sep (loc "verified/lib.rs(10,1-38)", CallExpr (loc "verified/lib.rs(10,1-38)", "thread_token", [], [], [VarPat (loc "verified/lib.rs(10,1-38)", "_t")], Static), Operation (loc "verified/lib.rs(10,1-38)", Eq, [Var (loc "verified/lib.rs(10,1-38)", "_t"); Var (loc "verified/lib.rs(10,1-38)", "currentThread")])), EmpAsn (loc "verified/lib.rs(10,1-38)")), ("outcome", SwitchExpr (loc "verified/lib.rs(10,1-38)", Var (loc "verified/lib.rs(10,1-38)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(10,1-38)", "returning", ["result"], Sep (loc "verified/lib.rs(10,1-38)", CallExpr (loc "verified/lib.rs(10,1-38)", "thread_token", [], [], [LitPat (Var (loc "verified/lib.rs(10,1-38)", "_t"))], Static), True (loc "verified/lib.rs(10,38)")));
      SwitchExprClause (loc "verified/lib.rs(10,1-38)", "unwinding", [], Sep (loc "verified/lib.rs(10,1-38)", CallExpr (loc "verified/lib.rs(10,1-38)", "thread_token", [], [], [LitPat (Var (loc "verified/lib.rs(10,1-38)", "_t"))], Static), EmpAsn (loc "verified/lib.rs(10,1-38)")))
    ], None)))), false, None, false, []);
    Func (loc "verified/lib.rs(10,1-13,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(10,38)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(10,38)", StructType ("std_tuple_0_", []))])), "origin_local_may_panic", [(ConstTypeExpr (loc "verified/lib.rs(10,27-31)", ManifestTypeExpr (loc "verified/lib.rs(10,27-31)", Bool)), "flag")], false, (None, None), Some ((True (loc "verified/lib.rs(11,9-13)"), ("outcome", SwitchExpr (loc "verified/lib.rs(10,38-11,65)", Var (loc "verified/lib.rs(10,38-11,65)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(11,27-31)", "returning", ["result"], True (loc "verified/lib.rs(11,27-31)"));
      SwitchExprClause (loc "verified/lib.rs(11,55-59)", "unwinding", [], True (loc "verified/lib.rs(11,55-59)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(10,1-13,2)", [(loc "verified/lib.rs(10,1-13,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(10,38)", StructType ("std_tuple_0_", []))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-13,2)", [(loc "verified/lib.rs(10,1-13,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-13,2)", ManifestTypeExpr (loc "verified/lib.rs(12,5-19)", StructType ("std_tuple_0_", [])))), "$_2", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-13,2)", [(loc "verified/lib.rs(10,1-13,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(12,14-18)", Bool)), "$_3", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-13,2)", [(loc "verified/lib.rs(10,1-13,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(12,5-19)", UnionType ("std_empty_"))), "$_4", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(12,5-19)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(12,5-19)", loc "verified/lib.rs(12,5-19)", "_2", "$_2");
      RustStorageLiveStmt (loc "verified/lib.rs(12,14-18)", loc "verified/lib.rs(12,14-18)", "_3", "$_3");
      ExprStmt (AssignExpr (loc "verified/lib.rs(12,14-18)", Var (loc "verified/lib.rs(12,14-18)", "$_3"), Mutation, Var (loc "verified/lib.rs(12,14-18)", "flag")));
      IfStmt (loc "verified/lib.rs(12,14-18)", Var (loc "verified/lib.rs(12,14-18)", "$_3"), [GotoStmt (loc "verified/lib.rs(12,14-18)", "1")], [GotoStmt (loc "verified/lib.rs(12,14-18)", "2")]);
      LabelStmt (loc "verified/lib.rs(12,18-19)", "2");
      RustStorageDeadStmt (loc "verified/lib.rs(12,18-19)", loc "verified/lib.rs(12,18-19)", "_3", "$_3");
      RustStorageDeadStmt (loc "verified/lib.rs(12,18-19)", loc "verified/lib.rs(12,18-19)", "_2", "$_2");
      ReturnStmt (loc "verified/lib.rs(13,2)", Some (CallExpr (loc "verified/lib.rs(13,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(13,2)", "$_0"))], Static)));
      LabelStmt (loc "verified/lib.rs(12,5-19)", "1");
      RustStorageLiveStmt (loc "verified/lib.rs(12,5-19)", loc "verified/lib.rs(12,5-19)", "_4", "$_4");
      ExprStmt (CallExpr (loc "verified/lib.rs(12,5-19)", "std::panicking::panic", [], [], [LitPat (StringLit (loc "<dummy location>", "assertion failed: !flag"))], Static));
      ReturnStmt (loc "verified/lib.rs(12,5-19)", Some (CallExpr (loc "verified/lib.rs(12,5-19)", "unwinding", [], [], [], Static)))
    ], loc "verified/lib.rs(13,1-2)")), false, []);
    Func (loc "verified/lib.rs(15,1-34,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(15,95-98)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(15,95-98)", Int (Unsigned, FixedWidthRank (3)))])), "origin_local_unwind_cleanup", [(ConstTypeExpr (loc "verified/lib.rs(15,43-48)", PtrTypeExpr (loc "verified/lib.rs(15,43-48)", ManifestTypeExpr (loc "verified/lib.rs(15,43-48)", Int (Unsigned, FixedWidthRank (3))))), "frame"); (ConstTypeExpr (loc "verified/lib.rs(15,62-66)", ManifestTypeExpr (loc "verified/lib.rs(15,62-66)", Bool)), "take"); (ConstTypeExpr (loc "verified/lib.rs(15,74-84)", ManifestTypeExpr (loc "verified/lib.rs(15,74-84)", Bool)), "panic_flag")], false, (None, None), Some ((CoefAsn (loc "verified/lib.rs(16,9-10)", VarPat (loc "verified/lib.rs(16,11-12)", "f"), PointsTo (loc "verified/lib.rs(16,21-24)", Deref (loc "verified/lib.rs(16,14-15)", Var (loc "verified/lib.rs(16,15-20)", "frame")), "RegularPointsTo", VarPat (loc "verified/lib.rs(16,26-32)", "framed"))), ("outcome", SwitchExpr (loc "verified/lib.rs(15,98-18,47)", Var (loc "verified/lib.rs(15,98-18,47)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(17,32-35)", "returning", ["result"], Sep (loc "verified/lib.rs(17,32-35)", CoefAsn (loc "verified/lib.rs(17,9-10)", LitPat (Var (loc "verified/lib.rs(17,10-11)", "f")), PointsTo (loc "verified/lib.rs(17,20-23)", Deref (loc "verified/lib.rs(17,13-14)", Var (loc "verified/lib.rs(17,14-19)", "frame")), "RegularPointsTo", LitPat (Var (loc "verified/lib.rs(17,24-30)", "framed")))), Operation (loc "verified/lib.rs(17,43-45)", Eq, [Var (loc "verified/lib.rs(17,36-42)", "result"); IntLit (loc "verified/lib.rs(17,46-47)", big_int_of_string "7", true, false, NoLSuffix)])));
      SwitchExprClause (loc "verified/lib.rs(18,19-20)", "unwinding", [], CoefAsn (loc "verified/lib.rs(18,19-20)", LitPat (Var (loc "verified/lib.rs(18,20-21)", "f")), PointsTo (loc "verified/lib.rs(18,30-33)", Deref (loc "verified/lib.rs(18,23-24)", Var (loc "verified/lib.rs(18,24-29)", "frame")), "RegularPointsTo", LitPat (Var (loc "verified/lib.rs(18,34-40)", "framed")))))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(15,95-98)", Int (Unsigned, FixedWidthRank (3)))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(19,9-12)", Int (Unsigned, FixedWidthRank (3))))), "tmp", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(20,5-36)", StructType ("std_tuple_0_", [])))), "$_5", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(21,5-36)", StructType ("std_tuple_0_", [])))), "$_6", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(22,5-36)", StructType ("std_tuple_0_", [])))), "$_7", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(23,5-36)", StructType ("std_tuple_0_", [])))), "$_8", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", PtrTypeExpr (loc "verified/lib.rs(24,9-10)", ManifestTypeExpr (loc "verified/lib.rs(24,9-10)", Int (Unsigned, FixedWidthRank (3)))))), "q", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", RustRefTypeExpr (loc "verified/lib.rs(24,13-18)", InferredTypeExpr (loc "verified/lib.rs(24,13-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(24,13-18)", Int (Unsigned, FixedWidthRank (3)))))), "$_10", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", RustRefTypeExpr (loc "verified/lib.rs(24,14-18)", InferredTypeExpr (loc "verified/lib.rs(24,14-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(24,14-18)", Int (Unsigned, FixedWidthRank (3)))))), "$_11", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (RustRefTypeExpr (loc "verified/lib.rs(24,15-18)", InferredTypeExpr (loc "verified/lib.rs(24,15-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(24,15-18)", Int (Unsigned, FixedWidthRank (3))))), "$_12", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(25,5-36)", StructType ("std_tuple_0_", [])))), "$_13", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(26,5-36)", StructType ("std_tuple_0_", [])))), "$_14", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(27,5-36)", StructType ("std_tuple_0_", [])))), "$_15", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(28,5-36)", StructType ("std_tuple_0_", [])))), "$_16", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(29,5-31,6)", StructType ("std_tuple_0_", [])))), "$_17", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(29,8-12)", Bool)), "$_18", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(30,9-43)", StructType ("std_tuple_0_", [])))), "$_19", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(30,32-42)", Bool)), "$_20", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(15,1-34,2)", [(loc "verified/lib.rs(15,1-34,2)", Some (ConstTypeExpr (loc "verified/lib.rs(15,1-34,2)", ManifestTypeExpr (loc "verified/lib.rs(32,9-15)", Int (Unsigned, FixedWidthRank (3))))), "result", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(19,9-12)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(19,9-12)", loc "verified/lib.rs(19,9-12)", "_4", "tmp");
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,15-39)", Var (loc "verified/lib.rs(19,15-39)", "tmp"), Initialization, CastExpr (loc "verified/lib.rs(19,33-38)", ManifestTypeExpr (loc "verified/lib.rs(19,33-38)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(19,33-38)", big_int_of_string "7", true, false, LLSuffix))));
      RustStorageLiveStmt (loc "verified/lib.rs(20,5-36)", loc "verified/lib.rs(20,5-36)", "_5", "$_5");
      PureStmt (loc "verified/lib.rs(20,5-21,1)", DeclStmt (loc "verified/lib.rs(20,9-12)", [(loc "verified/lib.rs(20,13-14)", None, "k", Some (CallExpr (loc "verified/lib.rs(20,17-31)", "begin_lifetime", [], [], [], Static)), (ref (false), ref (None)))]));
      RustStorageDeadStmt (loc "verified/lib.rs(20,36-37)", loc "verified/lib.rs(20,36-37)", "_5", "$_5");
      RustStorageLiveStmt (loc "verified/lib.rs(21,5-36)", loc "verified/lib.rs(21,5-36)", "_6", "$_6");
      PureStmt (loc "verified/lib.rs(21,5-22,1)", DeclStmt (loc "verified/lib.rs(21,9-12)", [
        (loc "verified/lib.rs(21,13-21)", None, "held_ref", Some (CallExpr (loc "verified/lib.rs(21,24-37)", "precreate_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(21,38-39)", Var (loc "verified/lib.rs(21,39-42)", "tmp")))], Static)), (ref (false), ref (None)))
      ]));
      RustStorageDeadStmt (loc "verified/lib.rs(21,36-37)", loc "verified/lib.rs(21,36-37)", "_6", "$_6");
      RustStorageLiveStmt (loc "verified/lib.rs(22,5-36)", loc "verified/lib.rs(22,5-36)", "_7", "$_7");
      PureStmt (loc "verified/lib.rs(22,5-23,1)", MergeFractionsStmt (loc "verified/lib.rs(22,9-24)", CallExpr (loc "verified/lib.rs(22,25-39)", "lifetime_token", [], [], [LitPat (Var (loc "verified/lib.rs(22,40-41)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(22,36-37)", loc "verified/lib.rs(22,36-37)", "_7", "$_7");
      RustStorageLiveStmt (loc "verified/lib.rs(23,5-36)", loc "verified/lib.rs(23,5-36)", "_8", "$_8");
      PureStmt (loc "verified/lib.rs(23,5-24,1)", ExprStmt (CallExpr (loc "verified/lib.rs(23,9-26)", "init_ref_readonly", [], [], [
        LitPat (Var (loc "verified/lib.rs(23,27-35)", "held_ref"));
        LitPat (Operation (loc "verified/lib.rs(23,38-39)", Div, [IntLit (loc "verified/lib.rs(23,37-38)", big_int_of_string "1", true, false, NoLSuffix); IntLit (loc "verified/lib.rs(23,39-40)", big_int_of_string "2", true, false, NoLSuffix)]))
      ], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(23,36-37)", loc "verified/lib.rs(23,36-37)", "_8", "$_8");
      RustStorageLiveStmt (loc "verified/lib.rs(24,9-10)", loc "verified/lib.rs(24,9-10)", "_9", "q");
      RustStorageLiveStmt (loc "verified/lib.rs(24,13-18)", loc "verified/lib.rs(24,13-18)", "_10", "$_10");
      RustStorageLiveStmt (loc "verified/lib.rs(24,14-18)", loc "verified/lib.rs(24,14-18)", "_11", "$_11");
      RustStorageLiveStmt (loc "verified/lib.rs(24,15-18)", loc "verified/lib.rs(24,15-18)", "_12", "$_12");
      ExprStmt (AssignExpr (loc "verified/lib.rs(24,15-18)", Var (loc "verified/lib.rs(24,15-18)", "$_12"), Mutation, CallExpr (loc "verified/lib.rs(24,15-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(24,15-18)", "create_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(24,15-18)", Var (loc "verified/lib.rs(24,15-18)", "tmp")))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(24,14-18)", Var (loc "verified/lib.rs(24,14-18)", "$_11"), Initialization, Var (loc "verified/lib.rs(24,14-18)", "$_12")));
      RustStorageDeadStmt (loc "verified/lib.rs(24,17-18)", loc "verified/lib.rs(24,17-18)", "_12", "$_12");
      ExprStmt (AssignExpr (loc "verified/lib.rs(24,13-18)", Var (loc "verified/lib.rs(24,13-18)", "$_10"), Initialization, CallExpr (loc "verified/lib.rs(24,13-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(24,13-18)", "reborrow_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(24,13-18)", Deref (loc "verified/lib.rs(24,13-18)", Var (loc "verified/lib.rs(24,13-18)", "$_11"))))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(24,13-18)", Var (loc "verified/lib.rs(24,13-18)", "q"), Initialization, AddressOf (loc "verified/lib.rs(24,13-18)", Deref (loc "verified/lib.rs(24,13-18)", Var (loc "verified/lib.rs(24,13-18)", "$_10")))));
      RustStorageDeadStmt (loc "verified/lib.rs(24,32-33)", loc "verified/lib.rs(24,32-33)", "_10", "$_10");
      RustStorageLiveStmt (loc "verified/lib.rs(25,5-36)", loc "verified/lib.rs(25,5-36)", "_13", "$_13");
      PureStmt (loc "verified/lib.rs(25,5-26,1)", Assert (loc "verified/lib.rs(25,9-15)", Operation (loc "verified/lib.rs(25,75-77)", Or, [
        Operation (loc "verified/lib.rs(25,57-59)", Le, [
          Operation (loc "verified/lib.rs(25,28-29)", Add, [CastExpr (loc "verified/lib.rs(25,19-21)", ManifestTypeExpr (loc "verified/lib.rs(25,22-27)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(25,17-18)", "q")); SizeofExpr (loc "verified/lib.rs(25,54-55)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(25,50-53)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(25,66-68)", ManifestTypeExpr (loc "verified/lib.rs(25,69-74)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(25,60-65)", "frame"))
        ]);
        Operation (loc "verified/lib.rs(25,122-124)", Le, [
          Operation (loc "verified/lib.rs(25,93-94)", Add, [CastExpr (loc "verified/lib.rs(25,84-86)", ManifestTypeExpr (loc "verified/lib.rs(25,87-92)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(25,78-83)", "frame")); SizeofExpr (loc "verified/lib.rs(25,119-120)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(25,115-118)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(25,127-129)", ManifestTypeExpr (loc "verified/lib.rs(25,130-135)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(25,125-126)", "q"))
        ])
      ])));
      RustStorageDeadStmt (loc "verified/lib.rs(25,36-37)", loc "verified/lib.rs(25,36-37)", "_13", "$_13");
      RustStorageLiveStmt (loc "verified/lib.rs(26,5-36)", loc "verified/lib.rs(26,5-36)", "_14", "$_14");
      PureStmt (loc "verified/lib.rs(26,5-27,1)", ExprStmt (CallExpr (loc "verified/lib.rs(26,9-25)", "end_ref_readonly", [], [], [LitPat (Var (loc "verified/lib.rs(26,26-34)", "held_ref"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(26,36-37)", loc "verified/lib.rs(26,36-37)", "_14", "$_14");
      RustStorageLiveStmt (loc "verified/lib.rs(27,5-36)", loc "verified/lib.rs(27,5-36)", "_15", "$_15");
      PureStmt (loc "verified/lib.rs(27,5-28,1)", MergeFractionsStmt (loc "verified/lib.rs(27,9-24)", CallExpr (loc "verified/lib.rs(27,41-42)", "points_to", [ManifestTypeExpr (loc "verified/lib.rs(27,37-40)", Int (Unsigned, FixedWidthRank (3)))], [], [LitPat (AddressOf (loc "verified/lib.rs(27,42-43)", Var (loc "verified/lib.rs(27,43-46)", "tmp"))); DummyPat], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(27,36-37)", loc "verified/lib.rs(27,36-37)", "_15", "$_15");
      RustStorageLiveStmt (loc "verified/lib.rs(28,5-36)", loc "verified/lib.rs(28,5-36)", "_16", "$_16");
      PureStmt (loc "verified/lib.rs(28,5-29,1)", ExprStmt (CallExpr (loc "verified/lib.rs(28,9-21)", "end_lifetime", [], [], [LitPat (Var (loc "verified/lib.rs(28,22-23)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(28,36-37)", loc "verified/lib.rs(28,36-37)", "_16", "$_16");
      RustStorageLiveStmt (loc "verified/lib.rs(29,5-31,6)", loc "verified/lib.rs(29,5-31,6)", "_17", "$_17");
      RustStorageLiveStmt (loc "verified/lib.rs(29,8-12)", loc "verified/lib.rs(29,8-12)", "_18", "$_18");
      ExprStmt (AssignExpr (loc "verified/lib.rs(29,8-12)", Var (loc "verified/lib.rs(29,8-12)", "$_18"), Mutation, Var (loc "verified/lib.rs(29,8-12)", "take")));
      IfStmt (loc "verified/lib.rs(29,8-12)", Var (loc "verified/lib.rs(29,8-12)", "$_18"), [GotoStmt (loc "verified/lib.rs(29,8-12)", "11")], [GotoStmt (loc "verified/lib.rs(29,8-12)", "13")]);
      LabelStmt (loc "verified/lib.rs(29,5-31,6)", "13");
      GotoStmt (loc "verified/lib.rs(29,5-31,6)", "14");
      LabelStmt (loc "verified/lib.rs(30,9-43)", "11");
      RustStorageLiveStmt (loc "verified/lib.rs(30,9-43)", loc "verified/lib.rs(30,9-43)", "_19", "$_19");
      RustStorageLiveStmt (loc "verified/lib.rs(30,32-42)", loc "verified/lib.rs(30,32-42)", "_20", "$_20");
      ExprStmt (AssignExpr (loc "verified/lib.rs(30,32-42)", Var (loc "verified/lib.rs(30,32-42)", "$_20"), Mutation, Var (loc "verified/lib.rs(30,32-42)", "panic_flag")));
      SwitchStmt (loc "verified/lib.rs(30,9-43)", CallExpr (loc "verified/lib.rs(30,9-43)", "origin_local_may_panic", [], [], [LitPat (Var (loc "verified/lib.rs(30,9-43)", "$_20"))], Static), [
        SwitchStmtClause (loc "verified/lib.rs(30,9-43)", CallExpr (loc "verified/lib.rs(30,9-43)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(30,9-43)", "__result"))], Static), [ExprStmt (AssignExpr (loc "verified/lib.rs(30,9-43)", Var (loc "verified/lib.rs(30,9-43)", "$_19"), Initialization, Var (loc "verified/lib.rs(30,9-43)", "__result")))]);
        SwitchStmtClause (loc "verified/lib.rs(30,9-43)", CallExpr (loc "verified/lib.rs(30,9-43)", "unwinding", [], [], [], Static), [ReturnStmt (loc "verified/lib.rs(30,9-43)", Some (CallExpr (loc "verified/lib.rs(30,9-43)", "unwinding", [], [], [], Static)))])
      ]);
      RustStorageDeadStmt (loc "verified/lib.rs(30,42-43)", loc "verified/lib.rs(30,42-43)", "_20", "$_20");
      RustStorageDeadStmt (loc "verified/lib.rs(30,43-44)", loc "verified/lib.rs(30,43-44)", "_19", "$_19");
      GotoStmt (loc "verified/lib.rs(29,5-31,6)", "14");
      LabelStmt (loc "verified/lib.rs(31,5-6)", "14");
      RustStorageDeadStmt (loc "verified/lib.rs(31,5-6)", loc "verified/lib.rs(31,5-6)", "_18", "$_18");
      RustStorageDeadStmt (loc "verified/lib.rs(31,5-6)", loc "verified/lib.rs(31,5-6)", "_17", "$_17");
      RustStorageLiveStmt (loc "verified/lib.rs(32,9-15)", loc "verified/lib.rs(32,9-15)", "_21", "result");
      ExprStmt (AssignExpr (loc "verified/lib.rs(32,27-29)", Var (loc "verified/lib.rs(32,27-29)", "result"), Initialization, Deref (loc "verified/lib.rs(32,27-29)", Var (loc "verified/lib.rs(32,27-29)", "q"))));
      ExprStmt (AssignExpr (loc "verified/lib.rs(33,5-11)", Var (loc "verified/lib.rs(33,5-11)", "$_0"), Mutation, Var (loc "verified/lib.rs(33,5-11)", "result")));
      RustStorageDeadStmt (loc "verified/lib.rs(34,1-2)", loc "verified/lib.rs(34,1-2)", "_21", "result");
      RustStorageDeadStmt (loc "verified/lib.rs(34,1-2)", loc "verified/lib.rs(34,1-2)", "_11", "$_11");
      RustStorageDeadStmt (loc "verified/lib.rs(34,1-2)", loc "verified/lib.rs(34,1-2)", "_9", "q");
      RustStorageDeadStmt (loc "verified/lib.rs(34,1-2)", loc "verified/lib.rs(34,1-2)", "_4", "tmp");
      ReturnStmt (loc "verified/lib.rs(34,2)", Some (CallExpr (loc "verified/lib.rs(34,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(34,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(34,1-2)")), false, [])
  ])
]