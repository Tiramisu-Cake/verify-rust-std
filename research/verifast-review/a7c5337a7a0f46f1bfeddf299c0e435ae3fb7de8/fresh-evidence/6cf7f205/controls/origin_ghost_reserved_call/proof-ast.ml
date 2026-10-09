[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(8,5-26)", Lemma (false, None), [], None, "vf__rust_storage_dead", [(ManifestTypeExpr (loc "verified/lib.rs(8,34-37)", Int (Unsigned, FixedWidthRank (3))), "value")], false, (None, None), Some ((True (loc "verified/lib.rs(9,9-13)"), ("result", True (loc "verified/lib.rs(10,9-13)")))), false, Some (([], loc "verified/lib.rs(12,1-2)")), false, []);
    Func (loc "verified/lib.rs(14,1-18,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(14,43)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(14,43)", StructType ("std_tuple_0_", []))])), "origin_ghost_reserved_call", [], false, (None, None), Some ((True (loc "verified/lib.rs(15,9-13)"), ("outcome", SwitchExpr (loc "verified/lib.rs(14,43-15,37)", Var (loc "verified/lib.rs(14,43-15,37)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(15,27-31)", "returning", ["result"], True (loc "verified/lib.rs(15,27-31)"));
      SwitchExprClause (loc "verified/lib.rs(14,43-15,37)", "unwinding", [], EmpAsn (loc "verified/lib.rs(14,43-15,37)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(14,1-18,2)", [(loc "verified/lib.rs(14,1-18,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(14,43)", StructType ("std_tuple_0_", []))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(14,1-18,2)", [(loc "verified/lib.rs(14,1-18,2)", Some (ConstTypeExpr (loc "verified/lib.rs(14,1-18,2)", ManifestTypeExpr (loc "verified/lib.rs(16,9-14)", Int (Unsigned, FixedWidthRank (3))))), "local", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(14,1-18,2)", [(loc "verified/lib.rs(14,1-18,2)", Some (ConstTypeExpr (loc "verified/lib.rs(14,1-18,2)", ManifestTypeExpr (loc "verified/lib.rs(17,5-36)", StructType ("std_tuple_0_", [])))), "$_2", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(16,9-14)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(16,9-14)", loc "verified/lib.rs(16,9-14)", "_1", "local");
      ExprStmt (AssignExpr (loc "verified/lib.rs(16,17-22)", Var (loc "verified/lib.rs(16,17-22)", "local"), Initialization, CastExpr (loc "verified/lib.rs(16,17-22)", ManifestTypeExpr (loc "verified/lib.rs(16,17-22)", Int (Unsigned, FixedWidthRank (3))), IntLit (loc "verified/lib.rs(16,17-22)", big_int_of_string "7", true, false, LLSuffix))));
      RustStorageLiveStmt (loc "verified/lib.rs(17,5-36)", loc "verified/lib.rs(17,5-36)", "_2", "$_2");
      PureStmt (loc "verified/lib.rs(17,5-96)", ExprStmt (CallExpr (loc "verified/lib.rs(17,9-30)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(17,31-36)", "local"))], Static)));
      RustStorageDeadStmt (loc "verified/lib.rs(17,36-37)", loc "verified/lib.rs(17,36-37)", "_2", "$_2");
      RustStorageDeadStmt (loc "verified/lib.rs(18,1-2)", loc "verified/lib.rs(18,1-2)", "_1", "local");
      ReturnStmt (loc "verified/lib.rs(18,2)", Some (CallExpr (loc "verified/lib.rs(18,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(18,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(18,1-2)")), false, [])
  ])
]