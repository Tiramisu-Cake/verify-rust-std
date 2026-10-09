[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(7,1-11,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(7,43)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(7,43)", StructType ("std_tuple_0_", []))])), "origin_unit_runtime_layout", [], false, (None, None), Some ((True (loc "verified/lib.rs(8,9-13)"), ("outcome", SwitchExpr (loc "verified/lib.rs(7,43-8,37)", Var (loc "verified/lib.rs(7,43-8,37)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(8,27-31)", "returning", ["result"], True (loc "verified/lib.rs(8,27-31)"));
      SwitchExprClause (loc "verified/lib.rs(7,43-8,37)", "unwinding", [], EmpAsn (loc "verified/lib.rs(7,43-8,37)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(7,1-11,2)", [(loc "verified/lib.rs(7,1-11,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(7,43)", StructType ("std_tuple_0_", []))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(7,1-11,2)", [(loc "verified/lib.rs(7,1-11,2)", Some (ConstTypeExpr (loc "verified/lib.rs(7,1-11,2)", ManifestTypeExpr (loc "verified/lib.rs(9,9-21)", Int (Unsigned, PtrRank)))), "runtime_size", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(7,1-11,2)", [(loc "verified/lib.rs(7,1-11,2)", Some (ConstTypeExpr (loc "verified/lib.rs(7,1-11,2)", ManifestTypeExpr (loc "verified/lib.rs(10,5-36)", StructType ("std_tuple_0_", [])))), "$_2", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(9,9-21)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(9,9-21)", loc "verified/lib.rs(9,9-21)", "_1", "runtime_size");
      SwitchStmt (loc "verified/lib.rs(9,24-50)", CallExpr (loc "verified/lib.rs(9,24-50)", "std::mem::size_of", [ManifestTypeExpr (loc "verified/lib.rs(9,24-50)", StructType ("std_tuple_0_", []))], [], [], Static), [
        SwitchStmtClause (loc "verified/lib.rs(9,24-50)", CallExpr (loc "verified/lib.rs(9,24-50)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(9,24-50)", "__result"))], Static), [ExprStmt (AssignExpr (loc "verified/lib.rs(9,24-50)", Var (loc "verified/lib.rs(9,24-50)", "runtime_size"), Initialization, Var (loc "verified/lib.rs(9,24-50)", "__result")))]);
        SwitchStmtClause (loc "verified/lib.rs(9,24-50)", CallExpr (loc "verified/lib.rs(9,24-50)", "unwinding", [], [], [], Static), [ReturnStmt (loc "verified/lib.rs(9,24-50)", Some (CallExpr (loc "verified/lib.rs(9,24-50)", "unwinding", [], [], [], Static)))])
      ]);
      RustStorageLiveStmt (loc "verified/lib.rs(10,5-36)", loc "verified/lib.rs(10,5-36)", "_2", "$_2");
      PureStmt (loc "verified/lib.rs(10,5-77)", Assert (loc "verified/lib.rs(10,9-15)", Operation (loc "verified/lib.rs(10,29-31)", Eq, [Var (loc "verified/lib.rs(10,16-28)", "runtime_size"); IntLit (loc "verified/lib.rs(10,32-33)", big_int_of_string "0", false, false, NoLSuffix)])));
      RustStorageDeadStmt (loc "verified/lib.rs(10,36-37)", loc "verified/lib.rs(10,36-37)", "_2", "$_2");
      RustStorageDeadStmt (loc "verified/lib.rs(11,1-2)", loc "verified/lib.rs(11,1-2)", "_1", "runtime_size");
      ReturnStmt (loc "verified/lib.rs(11,2)", Some (CallExpr (loc "verified/lib.rs(11,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(11,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(11,1-2)")), false, [])
  ])
]