[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(11,1-26,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(11,51-54)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(11,51-54)", Int (Unsigned, FixedWidthRank (3)))])), "span_positive", [(ConstTypeExpr (loc "verified/lib.rs(11,29-34)", PtrTypeExpr (loc "verified/lib.rs(11,29-34)", ManifestTypeExpr (loc "verified/lib.rs(11,29-34)", Int (Unsigned, FixedWidthRank (3))))), "frame")], false, (None, None), Some ((CoefAsn (loc "verified/lib.rs(12,9-10)", VarPat (loc "verified/lib.rs(12,11-12)", "f"), PointsTo (loc "verified/lib.rs(12,21-24)", Deref (loc "verified/lib.rs(12,14-15)", Var (loc "verified/lib.rs(12,15-20)", "frame")), "RegularPointsTo", VarPat (loc "verified/lib.rs(12,26-32)", "framed"))), ("outcome", SwitchExpr (loc "verified/lib.rs(11,54-13,53)", Var (loc "verified/lib.rs(11,54-13,53)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(13,32-35)", "returning", ["result"], Sep (loc "verified/lib.rs(13,32-35)", CoefAsn (loc "verified/lib.rs(13,9-10)", LitPat (Var (loc "verified/lib.rs(13,10-11)", "f")), PointsTo (loc "verified/lib.rs(13,20-23)", Deref (loc "verified/lib.rs(13,13-14)", Var (loc "verified/lib.rs(13,14-19)", "frame")), "RegularPointsTo", LitPat (Var (loc "verified/lib.rs(13,24-30)", "framed")))), Operation (loc "verified/lib.rs(13,43-45)", Eq, [Var (loc "verified/lib.rs(13,36-42)", "result"); IntLit (loc "verified/lib.rs(13,46-47)", big_int_of_string "7", true, false, NoLSuffix)])));
      SwitchExprClause (loc "verified/lib.rs(11,54-13,53)", "unwinding", [], EmpAsn (loc "verified/lib.rs(11,54-13,53)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(11,51-54)", Int (Unsigned, FixedWidthRank (3)))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(14,9-12)", Int (Unsigned, FixedWidthRank (3))))), "tmp", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(15,5-36)", StructType ("std_tuple_0_", [])))), "$_3", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(16,5-36)", StructType ("std_tuple_0_", [])))), "$_4", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(17,5-36)", StructType ("std_tuple_0_", [])))), "$_5", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(18,5-36)", StructType ("std_tuple_0_", [])))), "$_6", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", PtrTypeExpr (loc "verified/lib.rs(19,9-10)", ManifestTypeExpr (loc "verified/lib.rs(19,9-10)", Int (Unsigned, FixedWidthRank (3)))))), "q", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", RustRefTypeExpr (loc "verified/lib.rs(19,13-18)", InferredTypeExpr (loc "verified/lib.rs(19,13-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,13-18)", Int (Unsigned, FixedWidthRank (3)))))), "$_8", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", RustRefTypeExpr (loc "verified/lib.rs(19,14-18)", InferredTypeExpr (loc "verified/lib.rs(19,14-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,14-18)", Int (Unsigned, FixedWidthRank (3)))))), "$_9", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (RustRefTypeExpr (loc "verified/lib.rs(19,15-18)", InferredTypeExpr (loc "verified/lib.rs(19,15-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,15-18)", Int (Unsigned, FixedWidthRank (3))))), "$_10", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(20,5-36)", StructType ("std_tuple_0_", [])))), "$_11", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(21,9-15)", Int (Unsigned, FixedWidthRank (3))))), "result", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(22,5-36)", StructType ("std_tuple_0_", [])))), "$_13", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(23,5-36)", StructType ("std_tuple_0_", [])))), "$_14", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(11,1-26,2)", [(loc "verified/lib.rs(11,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(11,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(24,5-36)", StructType ("std_tuple_0_", [])))), "$_15", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(14,9-12)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(14,9-12)", loc "verified/lib.rs(14,9-12)", "_2", "tmp");
      ExprStmt (AssignExpr (loc "verified/lib.rs(14,15-39)", Var (loc "verified/lib.rs(14,15-39)", "tmp"), Initialization, CastExpr (loc "verified/lib.rs(14,33-38)", ManifestTypeExpr (loc "verified/lib.rs(14,33-38)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(14,33-38)", big_int_of_string "7", true, false, LLSuffix))));
      RustStorageLiveStmt (loc "verified/lib.rs(15,5-36)", loc "verified/lib.rs(15,5-36)", "_3", "$_3");
      PureStmt (loc "verified/lib.rs(15,5-16,1)", DeclStmt (loc "verified/lib.rs(15,9-12)", [(loc "verified/lib.rs(15,13-14)", None, "k", Some (CallExpr (loc "verified/lib.rs(15,17-31)", "begin_lifetime", [], [], [], Static)), (ref (false), ref (None)))]));
      RustStorageDeadStmt (loc "verified/lib.rs(15,36-37)", loc "verified/lib.rs(15,36-37)", "_3", "$_3");
      RustStorageLiveStmt (loc "verified/lib.rs(16,5-36)", loc "verified/lib.rs(16,5-36)", "_4", "$_4");
      PureStmt (loc "verified/lib.rs(16,5-17,1)", DeclStmt (loc "verified/lib.rs(16,9-12)", [
        (loc "verified/lib.rs(16,13-21)", None, "held_ref", Some (CallExpr (loc "verified/lib.rs(16,24-37)", "precreate_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(16,38-39)", Var (loc "verified/lib.rs(16,39-42)", "tmp")))], Static)), (ref (false), ref (None)))
      ]));
      RustStorageDeadStmt (loc "verified/lib.rs(16,36-37)", loc "verified/lib.rs(16,36-37)", "_4", "$_4");
      RustStorageLiveStmt (loc "verified/lib.rs(17,5-36)", loc "verified/lib.rs(17,5-36)", "_5", "$_5");
      PureStmt (loc "verified/lib.rs(17,5-18,1)", MergeFractionsStmt (loc "verified/lib.rs(17,9-24)", CallExpr (loc "verified/lib.rs(17,25-39)", "lifetime_token", [], [], [LitPat (Var (loc "verified/lib.rs(17,40-41)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(17,36-37)", loc "verified/lib.rs(17,36-37)", "_5", "$_5");
      RustStorageLiveStmt (loc "verified/lib.rs(18,5-36)", loc "verified/lib.rs(18,5-36)", "_6", "$_6");
      PureStmt (loc "verified/lib.rs(18,5-19,1)", ExprStmt (CallExpr (loc "verified/lib.rs(18,9-26)", "init_ref_readonly", [], [], [
        LitPat (Var (loc "verified/lib.rs(18,27-35)", "held_ref"));
        LitPat (Operation (loc "verified/lib.rs(18,38-39)", Div, [IntLit (loc "verified/lib.rs(18,37-38)", big_int_of_string "1", true, false, NoLSuffix); IntLit (loc "verified/lib.rs(18,39-40)", big_int_of_string "2", true, false, NoLSuffix)]))
      ], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(18,36-37)", loc "verified/lib.rs(18,36-37)", "_6", "$_6");
      RustStorageLiveStmt (loc "verified/lib.rs(19,9-10)", loc "verified/lib.rs(19,9-10)", "_7", "q");
      RustStorageLiveStmt (loc "verified/lib.rs(19,13-18)", loc "verified/lib.rs(19,13-18)", "_8", "$_8");
      RustStorageLiveStmt (loc "verified/lib.rs(19,14-18)", loc "verified/lib.rs(19,14-18)", "_9", "$_9");
      RustStorageLiveStmt (loc "verified/lib.rs(19,15-18)", loc "verified/lib.rs(19,15-18)", "_10", "$_10");
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,15-18)", Var (loc "verified/lib.rs(19,15-18)", "$_10"), Mutation, CallExpr (loc "verified/lib.rs(19,15-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(19,15-18)", "create_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(19,15-18)", Var (loc "verified/lib.rs(19,15-18)", "tmp")))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,14-18)", Var (loc "verified/lib.rs(19,14-18)", "$_9"), Initialization, Var (loc "verified/lib.rs(19,14-18)", "$_10")));
      RustStorageDeadStmt (loc "verified/lib.rs(19,17-18)", loc "verified/lib.rs(19,17-18)", "_10", "$_10");
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,13-18)", Var (loc "verified/lib.rs(19,13-18)", "$_8"), Initialization, CallExpr (loc "verified/lib.rs(19,13-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(19,13-18)", "reborrow_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(19,13-18)", Deref (loc "verified/lib.rs(19,13-18)", Var (loc "verified/lib.rs(19,13-18)", "$_9"))))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,13-18)", Var (loc "verified/lib.rs(19,13-18)", "q"), Initialization, AddressOf (loc "verified/lib.rs(19,13-18)", Deref (loc "verified/lib.rs(19,13-18)", Var (loc "verified/lib.rs(19,13-18)", "$_8")))));
      RustStorageDeadStmt (loc "verified/lib.rs(19,32-33)", loc "verified/lib.rs(19,32-33)", "_8", "$_8");
      RustStorageLiveStmt (loc "verified/lib.rs(20,5-36)", loc "verified/lib.rs(20,5-36)", "_11", "$_11");
      PureStmt (loc "verified/lib.rs(20,5-196)", Assert (loc "verified/lib.rs(20,9-15)", Operation (loc "verified/lib.rs(20,75-77)", Or, [
        Operation (loc "verified/lib.rs(20,57-59)", Le, [
          Operation (loc "verified/lib.rs(20,28-29)", Add, [CastExpr (loc "verified/lib.rs(20,19-21)", ManifestTypeExpr (loc "verified/lib.rs(20,22-27)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,17-18)", "q")); SizeofExpr (loc "verified/lib.rs(20,54-55)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(20,50-53)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(20,66-68)", ManifestTypeExpr (loc "verified/lib.rs(20,69-74)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,60-65)", "frame"))
        ]);
        Operation (loc "verified/lib.rs(20,122-124)", Le, [
          Operation (loc "verified/lib.rs(20,93-94)", Add, [CastExpr (loc "verified/lib.rs(20,84-86)", ManifestTypeExpr (loc "verified/lib.rs(20,87-92)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,78-83)", "frame")); SizeofExpr (loc "verified/lib.rs(20,119-120)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(20,115-118)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(20,127-129)", ManifestTypeExpr (loc "verified/lib.rs(20,130-135)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,125-126)", "q"))
        ])
      ])));
      RustStorageDeadStmt (loc "verified/lib.rs(20,36-37)", loc "verified/lib.rs(20,36-37)", "_11", "$_11");
      RustStorageLiveStmt (loc "verified/lib.rs(21,9-15)", loc "verified/lib.rs(21,9-15)", "_12", "result");
      ExprStmt (AssignExpr (loc "verified/lib.rs(21,27-29)", Var (loc "verified/lib.rs(21,27-29)", "result"), Initialization, Deref (loc "verified/lib.rs(21,27-29)", Var (loc "verified/lib.rs(21,27-29)", "q"))));
      RustStorageLiveStmt (loc "verified/lib.rs(22,5-36)", loc "verified/lib.rs(22,5-36)", "_13", "$_13");
      PureStmt (loc "verified/lib.rs(22,5-23,1)", ExprStmt (CallExpr (loc "verified/lib.rs(22,9-25)", "end_ref_readonly", [], [], [LitPat (Var (loc "verified/lib.rs(22,26-34)", "held_ref"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(22,36-37)", loc "verified/lib.rs(22,36-37)", "_13", "$_13");
      RustStorageLiveStmt (loc "verified/lib.rs(23,5-36)", loc "verified/lib.rs(23,5-36)", "_14", "$_14");
      PureStmt (loc "verified/lib.rs(23,5-24,1)", MergeFractionsStmt (loc "verified/lib.rs(23,9-24)", CallExpr (loc "verified/lib.rs(23,41-42)", "points_to", [ManifestTypeExpr (loc "verified/lib.rs(23,37-40)", Int (Unsigned, FixedWidthRank (3)))], [], [LitPat (AddressOf (loc "verified/lib.rs(23,42-43)", Var (loc "verified/lib.rs(23,43-46)", "tmp"))); DummyPat], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(23,36-37)", loc "verified/lib.rs(23,36-37)", "_14", "$_14");
      RustStorageLiveStmt (loc "verified/lib.rs(24,5-36)", loc "verified/lib.rs(24,5-36)", "_15", "$_15");
      PureStmt (loc "verified/lib.rs(24,5-25,1)", ExprStmt (CallExpr (loc "verified/lib.rs(24,9-21)", "end_lifetime", [], [], [LitPat (Var (loc "verified/lib.rs(24,22-23)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(24,36-37)", loc "verified/lib.rs(24,36-37)", "_15", "$_15");
      ExprStmt (AssignExpr (loc "verified/lib.rs(25,5-11)", Var (loc "verified/lib.rs(25,5-11)", "$_0"), Mutation, Var (loc "verified/lib.rs(25,5-11)", "result")));
      RustStorageDeadStmt (loc "verified/lib.rs(26,1-2)", loc "verified/lib.rs(26,1-2)", "_12", "result");
      RustStorageDeadStmt (loc "verified/lib.rs(26,1-2)", loc "verified/lib.rs(26,1-2)", "_9", "$_9");
      RustStorageDeadStmt (loc "verified/lib.rs(26,1-2)", loc "verified/lib.rs(26,1-2)", "_7", "q");
      RustStorageDeadStmt (loc "verified/lib.rs(26,1-2)", loc "verified/lib.rs(26,1-2)", "_2", "tmp");
      ReturnStmt (loc "verified/lib.rs(26,2)", Some (CallExpr (loc "verified/lib.rs(26,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(26,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(26,1-2)")), false, [])
  ])
]