[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(9,1-17,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(9,49-52)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(9,49-52)", Int (Unsigned, FixedWidthRank (3)))])), "origin_local_death_lost_cell", [], false, (None, None), Some ((True (loc "verified/lib.rs(10,9-13)"), ("outcome", SwitchExpr (loc "verified/lib.rs(9,52-10,44)", Var (loc "verified/lib.rs(9,52-10,44)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(10,34-36)", "returning", ["result"], Operation (loc "verified/lib.rs(10,34-36)", Eq, [Var (loc "verified/lib.rs(10,27-33)", "result"); IntLit (loc "verified/lib.rs(10,37-38)", big_int_of_string "9", true, false, NoLSuffix)]));
      SwitchExprClause (loc "verified/lib.rs(9,52-10,44)", "unwinding", [], EmpAsn (loc "verified/lib.rs(9,52-10,44)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(9,1-17,2)", [(loc "verified/lib.rs(9,1-17,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(9,49-52)", Int (Unsigned, FixedWidthRank (3)))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-17,2)", [(loc "verified/lib.rs(9,1-17,2)", Some (ConstTypeExpr (loc "verified/lib.rs(9,1-17,2)", ManifestTypeExpr (loc "verified/lib.rs(11,9-15)", Int (Unsigned, FixedWidthRank (3))))), "result", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-17,2)", [(loc "verified/lib.rs(9,1-17,2)", Some (ConstTypeExpr (loc "verified/lib.rs(9,1-17,2)", ManifestTypeExpr (loc "verified/lib.rs(12,13-16)", Int (Unsigned, FixedWidthRank (3))))), "tmp", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-17,2)", [(loc "verified/lib.rs(9,1-17,2)", Some (ConstTypeExpr (loc "verified/lib.rs(9,1-17,2)", ManifestTypeExpr (loc "verified/lib.rs(13,9-40)", StructType ("std_tuple_0_", [])))), "$_3", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(11,9-15)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(11,9-15)", loc "verified/lib.rs(11,9-15)", "_1", "result");
      RustStorageLiveStmt (loc "verified/lib.rs(12,13-16)", loc "verified/lib.rs(12,13-16)", "_2", "tmp");
      ExprStmt (AssignExpr (loc "verified/lib.rs(12,19-43)", Var (loc "verified/lib.rs(12,19-43)", "tmp"), Initialization, CastExpr (loc "verified/lib.rs(12,37-42)", ManifestTypeExpr (loc "verified/lib.rs(12,37-42)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(12,37-42)", big_int_of_string "7", true, false, LLSuffix))));
      RustStorageLiveStmt (loc "verified/lib.rs(13,9-40)", loc "verified/lib.rs(13,9-40)", "_3", "$_3");
      PureStmt (loc "verified/lib.rs(13,9-14,1)", Leak (loc "verified/lib.rs(13,13-17)", CoefAsn (loc "verified/lib.rs(13,18-19)", VarPat (loc "verified/lib.rs(13,20-21)", "f"), CallExpr (loc "verified/lib.rs(13,38-39)", "points_to", [ManifestTypeExpr (loc "verified/lib.rs(13,34-37)", Int (Unsigned, FixedWidthRank (3)))], [], [LitPat (AddressOf (loc "verified/lib.rs(13,39-40)", Var (loc "verified/lib.rs(13,40-43)", "tmp"))); DummyPat], Static))));
      RustStorageDeadStmt (loc "verified/lib.rs(13,40-41)", loc "verified/lib.rs(13,40-41)", "_3", "$_3");
      ExprStmt (AssignExpr (loc "verified/lib.rs(14,9-14)", Var (loc "verified/lib.rs(14,9-14)", "result"), Initialization, CastExpr (loc "verified/lib.rs(14,9-14)", ManifestTypeExpr (loc "verified/lib.rs(14,9-14)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(14,9-14)", big_int_of_string "9", true, false, LLSuffix))));
      RustStorageDeadStmt (loc "verified/lib.rs(15,5-6)", loc "verified/lib.rs(15,5-6)", "_2", "tmp");
      ExprStmt (AssignExpr (loc "verified/lib.rs(16,5-11)", Var (loc "verified/lib.rs(16,5-11)", "$_0"), Mutation, Var (loc "verified/lib.rs(16,5-11)", "result")));
      RustStorageDeadStmt (loc "verified/lib.rs(17,1-2)", loc "verified/lib.rs(17,1-2)", "_1", "result");
      ReturnStmt (loc "verified/lib.rs(17,2)", Some (CallExpr (loc "verified/lib.rs(17,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(17,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(17,1-2)")), false, [])
  ])
]