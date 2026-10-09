[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(10,1-27,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(10,52-55)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(10,52-55)", Int (Unsigned, FixedWidthRank (3)))])), "span_raw_arbitrary", [(ConstTypeExpr (loc "verified/lib.rs(10,34-35)", PtrTypeExpr (loc "verified/lib.rs(10,34-35)", ManifestTypeExpr (loc "verified/lib.rs(10,34-35)", Int (Unsigned, FixedWidthRank (3))))), "p")], false, (None, None), Some ((Sep (loc "verified/lib.rs(11,25-28)", Operation (loc "verified/lib.rs(11,20-22)", Neq, [CastExpr (loc "verified/lib.rs(11,11-13)", ManifestTypeExpr (loc "verified/lib.rs(11,14-19)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(11,9-10)", "p")); IntLit (loc "verified/lib.rs(11,23-24)", big_int_of_string "0", false, false, NoLSuffix)]), Sep (loc "verified/lib.rs(11,75-78)", Operation (loc "verified/lib.rs(11,70-72)", Eq, [
      Operation (loc "verified/lib.rs(11,40-41)", Mod, [CastExpr (loc "verified/lib.rs(11,31-33)", ManifestTypeExpr (loc "verified/lib.rs(11,34-39)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(11,29-30)", "p")); AlignofExpr (loc "verified/lib.rs(11,67-68)", ManifestTypeExpr (loc "verified/lib.rs(11,63-66)", Int (Unsigned, FixedWidthRank (3))))]);
      IntLit (loc "verified/lib.rs(11,73-74)", big_int_of_string "0", false, false, NoLSuffix)
    ]), Sep (loc "verified/lib.rs(12,73-76)", Operation (loc "verified/lib.rs(12,65-67)", Eq, [
      CallExpr (loc "verified/lib.rs(12,5-33)", "object_pointer_within_limits", [], [], [LitPat (Var (loc "verified/lib.rs(12,34-35)", "p")); LitPat (SizeofExpr (loc "verified/lib.rs(12,61-62)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(12,57-60)", Int (Unsigned, FixedWidthRank (3))))))], Static);
      True (loc "verified/lib.rs(12,68-72)")
    ]), Operation (loc "verified/lib.rs(13,16-18)", Le, [
      CastExpr (loc "verified/lib.rs(13,7-9)", ManifestTypeExpr (loc "verified/lib.rs(13,10-15)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(13,5-6)", "p"));
      Operation (loc "verified/lib.rs(13,30-31)", Sub, [Operation (loc "verified/lib.rs(13,19-24)", MaxValue (Int (Unsigned, PtrRank)), []); SizeofExpr (loc "verified/lib.rs(13,56-57)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(13,52-55)", Int (Unsigned, FixedWidthRank (3)))))])
    ])))), ("outcome", SwitchExpr (loc "verified/lib.rs(10,55-14,30)", Var (loc "verified/lib.rs(10,55-14,30)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(14,20-22)", "returning", ["result"], Operation (loc "verified/lib.rs(14,20-22)", Eq, [Var (loc "verified/lib.rs(14,13-19)", "result"); IntLit (loc "verified/lib.rs(14,23-24)", big_int_of_string "7", true, false, NoLSuffix)]));
      SwitchExprClause (loc "verified/lib.rs(10,55-14,30)", "unwinding", [], EmpAsn (loc "verified/lib.rs(10,55-14,30)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(10,52-55)", Int (Unsigned, FixedWidthRank (3)))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(15,9-12)", Int (Unsigned, FixedWidthRank (3))))), "tmp", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(16,5-36)", StructType ("std_tuple_0_", [])))), "$_3", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(17,5-36)", StructType ("std_tuple_0_", [])))), "$_4", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(18,5-36)", StructType ("std_tuple_0_", [])))), "$_5", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(19,5-36)", StructType ("std_tuple_0_", [])))), "$_6", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", PtrTypeExpr (loc "verified/lib.rs(20,9-10)", ManifestTypeExpr (loc "verified/lib.rs(20,9-10)", Int (Unsigned, FixedWidthRank (3)))))), "q", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", RustRefTypeExpr (loc "verified/lib.rs(20,13-18)", InferredTypeExpr (loc "verified/lib.rs(20,13-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(20,13-18)", Int (Unsigned, FixedWidthRank (3)))))), "$_8", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", RustRefTypeExpr (loc "verified/lib.rs(20,14-18)", InferredTypeExpr (loc "verified/lib.rs(20,14-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(20,14-18)", Int (Unsigned, FixedWidthRank (3)))))), "$_9", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (RustRefTypeExpr (loc "verified/lib.rs(20,15-18)", InferredTypeExpr (loc "verified/lib.rs(20,15-18)"), Shared, ManifestTypeExpr (loc "verified/lib.rs(20,15-18)", Int (Unsigned, FixedWidthRank (3))))), "$_10", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(21,5-36)", StructType ("std_tuple_0_", [])))), "$_11", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(22,9-15)", Int (Unsigned, FixedWidthRank (3))))), "result", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(23,5-36)", StructType ("std_tuple_0_", [])))), "$_13", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(24,5-36)", StructType ("std_tuple_0_", [])))), "$_14", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(10,1-27,2)", [(loc "verified/lib.rs(10,1-27,2)", Some (ConstTypeExpr (loc "verified/lib.rs(10,1-27,2)", ManifestTypeExpr (loc "verified/lib.rs(25,5-36)", StructType ("std_tuple_0_", [])))), "$_15", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(15,9-12)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(15,9-12)", loc "verified/lib.rs(15,9-12)", "_2", "tmp");
      ExprStmt (AssignExpr (loc "verified/lib.rs(15,15-39)", Var (loc "verified/lib.rs(15,15-39)", "tmp"), Initialization, CastExpr (loc "verified/lib.rs(15,33-38)", ManifestTypeExpr (loc "verified/lib.rs(15,33-38)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(15,33-38)", big_int_of_string "7", true, false, LLSuffix))));
      RustStorageLiveStmt (loc "verified/lib.rs(16,5-36)", loc "verified/lib.rs(16,5-36)", "_3", "$_3");
      PureStmt (loc "verified/lib.rs(16,5-17,1)", DeclStmt (loc "verified/lib.rs(16,9-12)", [(loc "verified/lib.rs(16,13-14)", None, "k", Some (CallExpr (loc "verified/lib.rs(16,17-31)", "begin_lifetime", [], [], [], Static)), (ref (false), ref (None)))]));
      RustStorageDeadStmt (loc "verified/lib.rs(16,36-37)", loc "verified/lib.rs(16,36-37)", "_3", "$_3");
      RustStorageLiveStmt (loc "verified/lib.rs(17,5-36)", loc "verified/lib.rs(17,5-36)", "_4", "$_4");
      PureStmt (loc "verified/lib.rs(17,5-18,1)", DeclStmt (loc "verified/lib.rs(17,9-12)", [
        (loc "verified/lib.rs(17,13-21)", None, "held_ref", Some (CallExpr (loc "verified/lib.rs(17,24-37)", "precreate_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(17,38-39)", Var (loc "verified/lib.rs(17,39-42)", "tmp")))], Static)), (ref (false), ref (None)))
      ]));
      RustStorageDeadStmt (loc "verified/lib.rs(17,36-37)", loc "verified/lib.rs(17,36-37)", "_4", "$_4");
      RustStorageLiveStmt (loc "verified/lib.rs(18,5-36)", loc "verified/lib.rs(18,5-36)", "_5", "$_5");
      PureStmt (loc "verified/lib.rs(18,5-19,1)", MergeFractionsStmt (loc "verified/lib.rs(18,9-24)", CallExpr (loc "verified/lib.rs(18,25-39)", "lifetime_token", [], [], [LitPat (Var (loc "verified/lib.rs(18,40-41)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(18,36-37)", loc "verified/lib.rs(18,36-37)", "_5", "$_5");
      RustStorageLiveStmt (loc "verified/lib.rs(19,5-36)", loc "verified/lib.rs(19,5-36)", "_6", "$_6");
      PureStmt (loc "verified/lib.rs(19,5-20,1)", ExprStmt (CallExpr (loc "verified/lib.rs(19,9-26)", "init_ref_readonly", [], [], [
        LitPat (Var (loc "verified/lib.rs(19,27-35)", "held_ref"));
        LitPat (Operation (loc "verified/lib.rs(19,38-39)", Div, [IntLit (loc "verified/lib.rs(19,37-38)", big_int_of_string "1", true, false, NoLSuffix); IntLit (loc "verified/lib.rs(19,39-40)", big_int_of_string "2", true, false, NoLSuffix)]))
      ], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(19,36-37)", loc "verified/lib.rs(19,36-37)", "_6", "$_6");
      RustStorageLiveStmt (loc "verified/lib.rs(20,9-10)", loc "verified/lib.rs(20,9-10)", "_7", "q");
      RustStorageLiveStmt (loc "verified/lib.rs(20,13-18)", loc "verified/lib.rs(20,13-18)", "_8", "$_8");
      RustStorageLiveStmt (loc "verified/lib.rs(20,14-18)", loc "verified/lib.rs(20,14-18)", "_9", "$_9");
      RustStorageLiveStmt (loc "verified/lib.rs(20,15-18)", loc "verified/lib.rs(20,15-18)", "_10", "$_10");
      ExprStmt (AssignExpr (loc "verified/lib.rs(20,15-18)", Var (loc "verified/lib.rs(20,15-18)", "$_10"), Mutation, CallExpr (loc "verified/lib.rs(20,15-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(20,15-18)", "create_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(20,15-18)", Var (loc "verified/lib.rs(20,15-18)", "tmp")))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(20,14-18)", Var (loc "verified/lib.rs(20,14-18)", "$_9"), Initialization, Var (loc "verified/lib.rs(20,14-18)", "$_10")));
      RustStorageDeadStmt (loc "verified/lib.rs(20,17-18)", loc "verified/lib.rs(20,17-18)", "_10", "$_10");
      ExprStmt (AssignExpr (loc "verified/lib.rs(20,13-18)", Var (loc "verified/lib.rs(20,13-18)", "$_8"), Initialization, CallExpr (loc "verified/lib.rs(20,13-18)", "fn_outcome_result", [], [], [
        LitPat (CallExpr (loc "verified/lib.rs(20,13-18)", "reborrow_ref", [], [], [LitPat (AddressOf (loc "verified/lib.rs(20,13-18)", Deref (loc "verified/lib.rs(20,13-18)", Var (loc "verified/lib.rs(20,13-18)", "$_9"))))], Static))
      ], Static)));
      ExprStmt (AssignExpr (loc "verified/lib.rs(20,13-18)", Var (loc "verified/lib.rs(20,13-18)", "q"), Initialization, AddressOf (loc "verified/lib.rs(20,13-18)", Deref (loc "verified/lib.rs(20,13-18)", Var (loc "verified/lib.rs(20,13-18)", "$_8")))));
      RustStorageDeadStmt (loc "verified/lib.rs(20,32-33)", loc "verified/lib.rs(20,32-33)", "_8", "$_8");
      RustStorageLiveStmt (loc "verified/lib.rs(21,5-36)", loc "verified/lib.rs(21,5-36)", "_11", "$_11");
      PureStmt (loc "verified/lib.rs(21,5-171)", Assert (loc "verified/lib.rs(21,9-15)", Operation (loc "verified/lib.rs(21,71-73)", Or, [
        Operation (loc "verified/lib.rs(21,57-59)", Le, [
          Operation (loc "verified/lib.rs(21,28-29)", Add, [CastExpr (loc "verified/lib.rs(21,19-21)", ManifestTypeExpr (loc "verified/lib.rs(21,22-27)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(21,17-18)", "q")); SizeofExpr (loc "verified/lib.rs(21,54-55)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(21,50-53)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(21,62-64)", ManifestTypeExpr (loc "verified/lib.rs(21,65-70)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(21,60-61)", "p"))
        ]);
        Operation (loc "verified/lib.rs(21,114-116)", Le, [
          Operation (loc "verified/lib.rs(21,85-86)", Add, [CastExpr (loc "verified/lib.rs(21,76-78)", ManifestTypeExpr (loc "verified/lib.rs(21,79-84)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(21,74-75)", "p")); SizeofExpr (loc "verified/lib.rs(21,111-112)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(21,107-110)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(21,119-121)", ManifestTypeExpr (loc "verified/lib.rs(21,122-127)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(21,117-118)", "q"))
        ])
      ])));
      RustStorageDeadStmt (loc "verified/lib.rs(21,36-37)", loc "verified/lib.rs(21,36-37)", "_11", "$_11");
      RustStorageLiveStmt (loc "verified/lib.rs(22,9-15)", loc "verified/lib.rs(22,9-15)", "_12", "result");
      ExprStmt (AssignExpr (loc "verified/lib.rs(22,27-29)", Var (loc "verified/lib.rs(22,27-29)", "result"), Initialization, Deref (loc "verified/lib.rs(22,27-29)", Var (loc "verified/lib.rs(22,27-29)", "q"))));
      RustStorageLiveStmt (loc "verified/lib.rs(23,5-36)", loc "verified/lib.rs(23,5-36)", "_13", "$_13");
      PureStmt (loc "verified/lib.rs(23,5-24,1)", ExprStmt (CallExpr (loc "verified/lib.rs(23,9-25)", "end_ref_readonly", [], [], [LitPat (Var (loc "verified/lib.rs(23,26-34)", "held_ref"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(23,36-37)", loc "verified/lib.rs(23,36-37)", "_13", "$_13");
      RustStorageLiveStmt (loc "verified/lib.rs(24,5-36)", loc "verified/lib.rs(24,5-36)", "_14", "$_14");
      PureStmt (loc "verified/lib.rs(24,5-25,1)", MergeFractionsStmt (loc "verified/lib.rs(24,9-24)", CallExpr (loc "verified/lib.rs(24,41-42)", "points_to", [ManifestTypeExpr (loc "verified/lib.rs(24,37-40)", Int (Unsigned, FixedWidthRank (3)))], [], [LitPat (AddressOf (loc "verified/lib.rs(24,42-43)", Var (loc "verified/lib.rs(24,43-46)", "tmp"))); DummyPat], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(24,36-37)", loc "verified/lib.rs(24,36-37)", "_14", "$_14");
      RustStorageLiveStmt (loc "verified/lib.rs(25,5-36)", loc "verified/lib.rs(25,5-36)", "_15", "$_15");
      PureStmt (loc "verified/lib.rs(25,5-26,1)", ExprStmt (CallExpr (loc "verified/lib.rs(25,9-21)", "end_lifetime", [], [], [LitPat (Var (loc "verified/lib.rs(25,22-23)", "k"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(25,36-37)", loc "verified/lib.rs(25,36-37)", "_15", "$_15");
      ExprStmt (AssignExpr (loc "verified/lib.rs(26,5-11)", Var (loc "verified/lib.rs(26,5-11)", "$_0"), Mutation, Var (loc "verified/lib.rs(26,5-11)", "result")));
      RustStorageDeadStmt (loc "verified/lib.rs(27,1-2)", loc "verified/lib.rs(27,1-2)", "_12", "result");
      RustStorageDeadStmt (loc "verified/lib.rs(27,1-2)", loc "verified/lib.rs(27,1-2)", "_9", "$_9");
      RustStorageDeadStmt (loc "verified/lib.rs(27,1-2)", loc "verified/lib.rs(27,1-2)", "_7", "q");
      RustStorageDeadStmt (loc "verified/lib.rs(27,1-2)", loc "verified/lib.rs(27,1-2)", "_2", "tmp");
      ReturnStmt (loc "verified/lib.rs(27,2)", Some (CallExpr (loc "verified/lib.rs(27,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(27,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(27,1-2)")), false, [])
  ])
]