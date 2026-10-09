[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(10,1-26,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(10,60-63)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(10,60-63)", Int (Unsigned, FixedWidthRank (3)))])), "span_lost_incoming_authority", [(ConstTypeExpr (loc "verified/lib.rs(10,44-45)", PtrTypeExpr (loc "verified/lib.rs(10,44-45)", ManifestTypeExpr (loc "verified/lib.rs(10,44-45)", Int (Unsigned, FixedWidthRank (3))))), "p")], false, (None, None), Some ((PointsTo (loc "verified/lib.rs(11,12-15)", Deref (loc "verified/lib.rs(11,9-10)", Var (loc "verified/lib.rs(11,10-11)", "p")), "RegularPointsTo", VarPat (loc "verified/lib.rs(11,17-25)", "incoming")), ("outcome", SwitchExpr (loc "verified/lib.rs(10,63-12,26)", Var (loc "verified/lib.rs(10,63-12,26)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(12,16-18)", "returning", ["result"], Operation (loc "verified/lib.rs(12,16-18)", Eq, [Var (loc "verified/lib.rs(12,9-15)", "result"); IntLit (loc "verified/lib.rs(12,19-20)", big_int_of_string "9", true, false, NoLSuffix)]));
      SwitchExprClause (loc "verified/lib.rs(10,63-12,26)", "unwinding", [], EmpAsn (loc "verified/lib.rs(10,63-12,26)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(10,60-63)", Int (Unsigned, FixedWidthRank (3)))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(13,5-36)", StructType ("std_tuple_0_", [])))), "$_2", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(14,9-12)", Int (Unsigned, FixedWidthRank (3))))), "tmp", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(15,5-36)", StructType ("std_tuple_0_", [])))), "$_4", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(16,5-36)", StructType ("std_tuple_0_", [])))), "$_5", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(17,5-36)", StructType ("std_tuple_0_", [])))), "$_6", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(18,5-36)", StructType ("std_tuple_0_", [])))), "$_7", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", PtrTypeExpr (loc "verified/lib.rs(19,9-10)", ManifestTypeExpr (loc "verified/lib.rs(19,9-10)", Int (Unsigned, FixedWidthRank (3)))))), "q", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", RustRefTypeExpr (loc "verified/lib.rs(19,13-18)", InferredTypeExpr (loc "verified/lib.rs(19,13-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,13-18)", Int (Unsigned, FixedWidthRank (3)))))), "$_9", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", RustRefTypeExpr (loc "verified/lib.rs(19,14-18)", InferredTypeExpr (loc "verified/lib.rs(19,14-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,14-18)", Int (Unsigned, FixedWidthRank (3)))))), "$_10", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (RustRefTypeExpr (loc "verified/lib.rs(19,15-18)", InferredTypeExpr (loc "verified/lib.rs(19,15-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(19,15-18)", Int (Unsigned, FixedWidthRank (3))))), "$_11", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(20,5-36)", StructType ("std_tuple_0_", [])))), "$_12", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(21,9-15)", Int (Unsigned, FixedWidthRank (3))))), "result", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(22,5-36)", StructType ("std_tuple_0_", [])))), "$_14", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(23,5-36)", StructType ("std_tuple_0_", [])))), "$_15", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-26,2)", [(loc "verified/lib.rs(10,1-26,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-26,2)", ManifestTypeExpr (loc "verified/lib.rs(24,5-36)", StructType ("std_tuple_0_", [])))), "$_16", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(13,5-36)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(13,5-36)", loc "verified/lib.rs(13,5-36)", "_2", "$_2");
      PureStmt (loc "verified/lib.rs(13,5-14,1)", Leak (loc "verified/lib.rs(13,9-13)", PointsTo (loc "verified/lib.rs(13,17-20)", Deref (loc "verified/lib.rs(13,14-15)", Var (loc "verified/lib.rs(13,15-16)", "p")), "RegularPointsTo", LitPat (Var (loc "verified/lib.rs(13,21-29)", "incoming")))));
      RustStorageDeadStmt (loc "verified/lib.rs(13,36-37)", loc "verified/lib.rs(13,36-37)", "_2", "$_2");
      RustStorageLiveStmt (loc "verified/lib.rs(14,9-12)", loc "verified/lib.rs(14,9-12)", "_3", "tmp");
      ExprStmt (AssignExpr (loc "verified/lib.rs(14,15-39)", Var (loc "verified/lib.rs(14,15-39)", "tmp"), Initialization, CastExpr (loc "verified/lib.rs(14,33-38)", ManifestTypeExpr (loc "verified/lib.rs(14,33-38)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(14,33-38)", big_int_of_string "9", true, false, LLSuffix))));
      RustStorageLiveStmt (loc "verified/lib.rs(15,5-36)", loc "verified/lib.rs(15,5-36)", "_4", "$_4");
      PureStmt (loc "verified/lib.rs(15,5-16,1)", DeclStmt (loc "verified/lib.rs(15,9-12)", [(loc "verified/lib.rs(15,13-14)", None, "k", Some (CallExpr (loc "verified/lib.rs(15,17-31)", "begin_lifetime", [], [], [], Static)), (ref (false), ref (None)))]));
      RustStorageDeadStmt (loc "verified/lib.rs(15,36-37)", loc "verified/lib.rs(15,36-37)", "_4", "$_4");
      RustStorageLiveStmt (loc "verified/lib.rs(16,5-36)", loc "verified/lib.rs(16,5-36)", "_5", "$_5");
      PureStmt (loc "verified/lib.rs(16,5-17,1)", DeclStmt (loc "verified/lib.rs(16,9-12)", [
        (loc "verified/lib.rs(16,13-21)", None, "held_ref", Some (CallExpr (loc "verified/lib.rs(16,24-37)", "precreate_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(16,38-39)", Var (loc "verified/lib.rs(16,39-42)", "tmp")))], Static)), (ref (false), ref (None)))
      ]));
      RustStorageDeadStmt (loc "verified/lib.rs(16,36-37)", loc "verified/lib.rs(16,36-37)", "_5", "$_5");
      RustStorageLiveStmt (loc "verified/lib.rs(17,5-36)", loc "verified/lib.rs(17,5-36)", "_6", "$_6");
      PureStmt (loc "verified/lib.rs(17,5-18,1)", MergeFractionsStmt (loc "verified/lib.rs(17,9-24)", CallExpr (loc "verified/lib.rs(17,25-39)", "lifetime_token", [], [], [LitPat (Var (loc "verified/lib.rs(17,40-41)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(17,36-37)", loc "verified/lib.rs(17,36-37)", "_6", "$_6");
      RustStorageLiveStmt (loc "verified/lib.rs(18,5-36)", loc "verified/lib.rs(18,5-36)", "_7", "$_7");
      PureStmt (loc "verified/lib.rs(18,5-19,1)", ExprStmt (CallExpr (loc "verified/lib.rs(18,9-26)", "init_ref_readonly", [], [], [
        LitPat (Var (loc "verified/lib.rs(18,27-35)", "held_ref"));
        LitPat (Operation (loc "verified/lib.rs(18,38-39)", Div, [IntLit (loc "verified/lib.rs(18,37-38)", big_int_of_string "1", true, false, NoLSuffix); IntLit (loc "verified/lib.rs(18,39-40)", big_int_of_string "2", true, false, NoLSuffix)]))
      ], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(18,36-37)", loc "verified/lib.rs(18,36-37)", "_7", "$_7");
      RustStorageLiveStmt (loc "verified/lib.rs(19,9-10)", loc "verified/lib.rs(19,9-10)", "_8", "q");
      RustStorageLiveStmt (loc "verified/lib.rs(19,13-18)", loc "verified/lib.rs(19,13-18)", "_9", "$_9");
      RustStorageLiveStmt (loc "verified/lib.rs(19,14-18)", loc "verified/lib.rs(19,14-18)", "_10", "$_10");
      RustStorageLiveStmt (loc "verified/lib.rs(19,15-18)", loc "verified/lib.rs(19,15-18)", "_11", "$_11");
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,15-18)", Var (loc "verified/lib.rs(19,15-18)", "$_11"), Mutation, CallExpr (loc "verified/lib.rs(19,15-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(19,15-18)", "create_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(19,15-18)", Var (loc "verified/lib.rs(19,15-18)", "tmp")))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,14-18)", Var (loc "verified/lib.rs(19,14-18)", "$_10"), Initialization, Var (loc "verified/lib.rs(19,14-18)", "$_11")));
      RustStorageDeadStmt (loc "verified/lib.rs(19,17-18)", loc "verified/lib.rs(19,17-18)", "_11", "$_11");
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,13-18)", Var (loc "verified/lib.rs(19,13-18)", "$_9"), Initialization, CallExpr (loc "verified/lib.rs(19,13-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(19,13-18)", "reborrow_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(19,13-18)", Deref (loc "verified/lib.rs(19,13-18)", Var (loc "verified/lib.rs(19,13-18)", "$_10"))))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,13-18)", Var (loc "verified/lib.rs(19,13-18)", "q"), Initialization, AddressOf (loc "verified/lib.rs(19,13-18)", Deref (loc "verified/lib.rs(19,13-18)", Var (loc "verified/lib.rs(19,13-18)", "$_9")))));
      RustStorageDeadStmt (loc "verified/lib.rs(19,32-33)", loc "verified/lib.rs(19,32-33)", "_9", "$_9");
      RustStorageLiveStmt (loc "verified/lib.rs(20,5-36)", loc "verified/lib.rs(20,5-36)", "_12", "$_12");
      PureStmt (loc "verified/lib.rs(20,5-196)", Assert (loc "verified/lib.rs(20,9-15)", Operation (loc "verified/lib.rs(20,71-73)", Or, [
        Operation (loc "verified/lib.rs(20,57-59)", Le, [
          Operation (loc "verified/lib.rs(20,28-29)", Add, [CastExpr (loc "verified/lib.rs(20,19-21)", ManifestTypeExpr (loc "verified/lib.rs(20,22-27)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,17-18)", "q")); SizeofExpr (loc "verified/lib.rs(20,54-55)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(20,50-53)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(20,62-64)", ManifestTypeExpr (loc "verified/lib.rs(20,65-70)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,60-61)", "p"))
        ]);
        Operation (loc "verified/lib.rs(20,114-116)", Le, [
          Operation (loc "verified/lib.rs(20,85-86)", Add, [CastExpr (loc "verified/lib.rs(20,76-78)", ManifestTypeExpr (loc "verified/lib.rs(20,79-84)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,74-75)", "p")); SizeofExpr (loc "verified/lib.rs(20,111-112)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(20,107-110)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(20,119-121)", ManifestTypeExpr (loc "verified/lib.rs(20,122-127)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,117-118)", "q"))
        ])
      ])));
      RustStorageDeadStmt (loc "verified/lib.rs(20,36-37)", loc "verified/lib.rs(20,36-37)", "_12", "$_12");
      RustStorageLiveStmt (loc "verified/lib.rs(21,9-15)", loc "verified/lib.rs(21,9-15)", "_13", "result");
      ExprStmt (AssignExpr (loc "verified/lib.rs(21,27-29)", Var (loc "verified/lib.rs(21,27-29)", "result"), Initialization, Deref (loc "verified/lib.rs(21,27-29)", Var (loc "verified/lib.rs(21,27-29)", "q"))));
      RustStorageLiveStmt (loc "verified/lib.rs(22,5-36)", loc "verified/lib.rs(22,5-36)", "_14", "$_14");
      PureStmt (loc "verified/lib.rs(22,5-23,1)", ExprStmt (CallExpr (loc "verified/lib.rs(22,9-25)", "end_ref_readonly", [], [], [LitPat (Var (loc "verified/lib.rs(22,26-34)", "held_ref"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(22,36-37)", loc "verified/lib.rs(22,36-37)", "_14", "$_14");
      RustStorageLiveStmt (loc "verified/lib.rs(23,5-36)", loc "verified/lib.rs(23,5-36)", "_15", "$_15");
      PureStmt (loc "verified/lib.rs(23,5-24,1)", MergeFractionsStmt (loc "verified/lib.rs(23,9-24)", CallExpr (loc "verified/lib.rs(23,41-42)", "points_to", [ManifestTypeExpr (loc "verified/lib.rs(23,37-40)", Int (Unsigned, FixedWidthRank (3)))], [], [LitPat (AddressOf (loc "verified/lib.rs(23,42-43)", Var (loc "verified/lib.rs(23,43-46)", "tmp"))); DummyPat], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(23,36-37)", loc "verified/lib.rs(23,36-37)", "_15", "$_15");
      RustStorageLiveStmt (loc "verified/lib.rs(24,5-36)", loc "verified/lib.rs(24,5-36)", "_16", "$_16");
      PureStmt (loc "verified/lib.rs(24,5-25,1)", ExprStmt (CallExpr (loc "verified/lib.rs(24,9-21)", "end_lifetime", [], [], [LitPat (Var (loc "verified/lib.rs(24,22-23)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(24,36-37)", loc "verified/lib.rs(24,36-37)", "_16", "$_16");
      ExprStmt (AssignExpr (loc "verified/lib.rs(25,5-11)", Var (loc "verified/lib.rs(25,5-11)", "$_0"), Mutation, Var (loc "verified/lib.rs(25,5-11)", "result")));
      RustStorageDeadStmt (loc "verified/lib.rs(26,1-2)", loc "verified/lib.rs(26,1-2)", "_13", "result");
      RustStorageDeadStmt (loc "verified/lib.rs(26,1-2)", loc "verified/lib.rs(26,1-2)", "_10", "$_10");
      RustStorageDeadStmt (loc "verified/lib.rs(26,1-2)", loc "verified/lib.rs(26,1-2)", "_8", "q");
      RustStorageDeadStmt (loc "verified/lib.rs(26,1-2)", loc "verified/lib.rs(26,1-2)", "_3", "tmp");
      ReturnStmt (loc "verified/lib.rs(26,2)", Some (CallExpr (loc "verified/lib.rs(26,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(26,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(26,1-2)")), false, [])
  ])
]