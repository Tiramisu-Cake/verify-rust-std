[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(7,1-10,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(7,38)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(7,38)", StructType ("std_tuple_0_", []))])), "vf__rust_storage_dead", [(ConstTypeExpr (loc "verified/lib.rs(7,26-27)", PtrTypeExpr (loc "verified/lib.rs(7,26-27)", ManifestTypeExpr (loc "verified/lib.rs(7,26-27)", Int (Unsigned, FixedWidthRank (3))))), "p")], false, (None, None), Some ((Sep (loc "verified/lib.rs(7,1-38)", Sep (loc "verified/lib.rs(7,1-38)", CallExpr (loc "verified/lib.rs(7,1-38)", "thread_token", [], [], [VarPat (loc "verified/lib.rs(7,1-38)", "_t")], Static), Operation (loc "verified/lib.rs(7,1-38)", Eq, [Var (loc "verified/lib.rs(7,1-38)", "_t"); Var (loc "verified/lib.rs(7,1-38)", "currentThread")])), EmpAsn (loc "verified/lib.rs(7,1-38)")), ("outcome", SwitchExpr (loc "verified/lib.rs(7,1-38)", Var (loc "verified/lib.rs(7,1-38)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(7,1-38)", "returning", ["result"], Sep (loc "verified/lib.rs(7,1-38)", CallExpr (loc "verified/lib.rs(7,1-38)", "thread_token", [], [], [LitPat (Var (loc "verified/lib.rs(7,1-38)", "_t"))], Static), True (loc "verified/lib.rs(7,38)")));
      SwitchExprClause (loc "verified/lib.rs(7,1-38)", "unwinding", [], Sep (loc "verified/lib.rs(7,1-38)", CallExpr (loc "verified/lib.rs(7,1-38)", "thread_token", [], [], [LitPat (Var (loc "verified/lib.rs(7,1-38)", "_t"))], Static), EmpAsn (loc "verified/lib.rs(7,1-38)")))
    ], None)))), false, None, false, []);
    Func (loc "verified/lib.rs(7,1-10,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(7,38)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(7,38)", StructType ("std_tuple_0_", []))])), "vf__rust_storage_dead", [(ConstTypeExpr (loc "verified/lib.rs(7,26-27)", PtrTypeExpr (loc "verified/lib.rs(7,26-27)", ManifestTypeExpr (loc "verified/lib.rs(7,26-27)", Int (Unsigned, FixedWidthRank (3))))), "p")], false, (None, None), Some ((PointsTo (loc "verified/lib.rs(8,12-15)", Deref (loc "verified/lib.rs(8,9-10)", Var (loc "verified/lib.rs(8,10-11)", "p")), "RegularPointsTo", VarPat (loc "verified/lib.rs(8,17-18)", "v")), ("outcome", SwitchExpr (loc "verified/lib.rs(7,38-8,46)", Var (loc "verified/lib.rs(7,38-8,46)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(8,35-38)", "returning", ["result"], PointsTo (loc "verified/lib.rs(8,35-38)", Deref (loc "verified/lib.rs(8,32-33)", Var (loc "verified/lib.rs(8,33-34)", "p")), "RegularPointsTo", LitPat (Var (loc "verified/lib.rs(8,39-40)", "v"))));
      SwitchExprClause (loc "verified/lib.rs(7,38-8,46)", "unwinding", [], EmpAsn (loc "verified/lib.rs(7,38-8,46)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(7,1-10,2)", [(loc "verified/lib.rs(7,1-10,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(7,38)", StructType ("std_tuple_0_", []))), "$_0", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(10,2)", "0");
      ReturnStmt (loc "verified/lib.rs(10,2)", Some (CallExpr (loc "verified/lib.rs(10,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(10,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(10,1-2)")), false, []);
    Func (loc "verified/lib.rs(12,1-15,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(12,66)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(12,66)", StructType ("std_tuple_0_", []))])), "origin_reserved_dead_requires_resource", [(ConstTypeExpr (loc "verified/lib.rs(12,54-55)", PtrTypeExpr (loc "verified/lib.rs(12,54-55)", ManifestTypeExpr (loc "verified/lib.rs(12,54-55)", Int (Unsigned, FixedWidthRank (3))))), "p")], false, (None, None), Some ((True (loc "verified/lib.rs(13,9-13)"), ("outcome", SwitchExpr (loc "verified/lib.rs(12,66-13,37)", Var (loc "verified/lib.rs(12,66-13,37)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(13,27-31)", "returning", ["result"], True (loc "verified/lib.rs(13,27-31)"));
      SwitchExprClause (loc "verified/lib.rs(12,66-13,37)", "unwinding", [], EmpAsn (loc "verified/lib.rs(12,66-13,37)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(12,1-15,2)", [(loc "verified/lib.rs(12,1-15,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(12,66)", StructType ("std_tuple_0_", []))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(12,1-15,2)", [(loc "verified/lib.rs(12,1-15,2)", Some (ConstTypeExpr (loc "verified/lib.rs(12,1-15,2)", ManifestTypeExpr (loc "verified/lib.rs(14,5-29)", StructType ("std_tuple_0_", [])))), "$_2", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(12,1-15,2)", [(loc "verified/lib.rs(12,1-15,2)", Some (PtrTypeExpr (loc "verified/lib.rs(14,27-28)", ManifestTypeExpr (loc "verified/lib.rs(14,27-28)", Int (Unsigned, FixedWidthRank (3))))), "$_3", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(14,5-29)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(14,5-29)", loc "verified/lib.rs(14,5-29)", "_2", "$_2");
      RustStorageLiveStmt (loc "verified/lib.rs(14,27-28)", loc "verified/lib.rs(14,27-28)", "_3", "$_3");
      ExprStmt (AssignExpr (loc "verified/lib.rs(14,27-28)", Var (loc "verified/lib.rs(14,27-28)", "$_3"), Mutation, Var (loc "verified/lib.rs(14,27-28)", "p")));
      SwitchStmt (loc "verified/lib.rs(14,5-29)", CallExpr (loc "verified/lib.rs(14,5-29)", "vf__rust_storage_dead", [], [], [LitPat (Var (loc "verified/lib.rs(14,5-29)", "$_3"))], Static), [
        SwitchStmtClause (loc "verified/lib.rs(14,5-29)", CallExpr (loc "verified/lib.rs(14,5-29)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(14,5-29)", "__result"))], Static), [ExprStmt (AssignExpr (loc "verified/lib.rs(14,5-29)", Var (loc "verified/lib.rs(14,5-29)", "$_2"), Initialization, Var (loc "verified/lib.rs(14,5-29)", "__result")))]);
        SwitchStmtClause (loc "verified/lib.rs(14,5-29)", CallExpr (loc "verified/lib.rs(14,5-29)", "unwinding", [], [], [], Static), [ReturnStmt (loc "verified/lib.rs(14,5-29)", Some (CallExpr (loc "verified/lib.rs(14,5-29)", "unwinding", [], [], [], Static)))])
      ]);
      RustStorageDeadStmt (loc "verified/lib.rs(14,28-29)", loc "verified/lib.rs(14,28-29)", "_3", "$_3");
      RustStorageDeadStmt (loc "verified/lib.rs(14,29-30)", loc "verified/lib.rs(14,29-30)", "_2", "$_2");
      ReturnStmt (loc "verified/lib.rs(15,2)", Some (CallExpr (loc "verified/lib.rs(15,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(15,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(15,1-2)")), false, [])
  ])
]