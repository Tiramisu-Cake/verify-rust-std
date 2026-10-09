[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(7,1-10,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(7,35)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(7,35)", StructType ("std_tuple_0_", []))])), "origin_unit_layout", [], false, (None, None), Some ((True (loc "verified/lib.rs(8,9-13)"), ("outcome", SwitchExpr (loc "verified/lib.rs(7,35-8,37)", Var (loc "verified/lib.rs(7,35-8,37)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(8,27-31)", "returning", ["result"], True (loc "verified/lib.rs(8,27-31)"));
      SwitchExprClause (loc "verified/lib.rs(7,35-8,37)", "unwinding", [], EmpAsn (loc "verified/lib.rs(7,35-8,37)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(7,1-10,2)", [(loc "verified/lib.rs(7,1-10,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(7,35)", StructType ("std_tuple_0_", []))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(7,1-10,2)", [(loc "verified/lib.rs(7,1-10,2)", Some (ConstTypeExpr (loc "verified/lib.rs(7,1-10,2)", ManifestTypeExpr (loc "verified/lib.rs(9,5-36)", StructType ("std_tuple_0_", [])))), "$_1", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(9,5-36)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(9,5-36)", loc "verified/lib.rs(9,5-36)", "_1", "$_1");
      PureStmt (loc "verified/lib.rs(9,5-82)", Assert (loc "verified/lib.rs(9,9-15)", Operation (loc "verified/lib.rs(9,42-44)", Eq, [SizeofExpr (loc "verified/lib.rs(9,39-40)", TypeExpr (StructTypeExpr (loc "verified/lib.rs(9,36-37)", Some ("std_tuple_0_"), None, [], []))); IntLit (loc "verified/lib.rs(9,45-46)", big_int_of_string "0", false, false, NoLSuffix)])));
      RustStorageDeadStmt (loc "verified/lib.rs(9,36-37)", loc "verified/lib.rs(9,36-37)", "_1", "$_1");
      ReturnStmt (loc "verified/lib.rs(10,2)", Some (CallExpr (loc "verified/lib.rs(10,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(10,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(10,1-2)")), false, [])
  ])
]