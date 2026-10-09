[
  PackageDecl (loc "<dummy location>", "", [], [
    Func (loc "verified/lib.rs(9,1-21,2)", Regular, [], Some (ConstructedTypeExpr (loc "verified/lib.rs(9,42)", "fn_outcome", [ManifestTypeExpr (loc "verified/lib.rs(9,42)", StructType ("std_tuple_0_", []))])), "span_overlap", [(ConstTypeExpr (loc "verified/lib.rs(9,28-29)", PtrTypeExpr (loc "verified/lib.rs(9,28-29)", ManifestTypeExpr (loc "verified/lib.rs(9,28-29)", Int (Unsigned, FixedWidthRank (3))))), "p")], false, (None, None), Some ((Sep (loc "verified/lib.rs(10,40-43)", Operation (loc "verified/lib.rs(10,11-12)", Lt, [IntLit (loc "verified/lib.rs(10,9-10)", big_int_of_string "0", false, false, NoLSuffix); SizeofExpr (loc "verified/lib.rs(10,37-38)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(10,33-36)", Int (Unsigned, FixedWidthRank (3)))))]), Sep (loc "verified/lib.rs(10,60-63)", Operation (loc "verified/lib.rs(10,55-57)", Neq, [CastExpr (loc "verified/lib.rs(10,46-48)", ManifestTypeExpr (loc "verified/lib.rs(10,49-54)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(10,44-45)", "p")); IntLit (loc "verified/lib.rs(10,58-59)", big_int_of_string "0", false, false, NoLSuffix)]), Sep (loc "verified/lib.rs(11,51-54)", Operation (loc "verified/lib.rs(11,46-48)", Eq, [
      Operation (loc "verified/lib.rs(11,16-17)", Mod, [CastExpr (loc "verified/lib.rs(11,7-9)", ManifestTypeExpr (loc "verified/lib.rs(11,10-15)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(11,5-6)", "p")); AlignofExpr (loc "verified/lib.rs(11,43-44)", ManifestTypeExpr (loc "verified/lib.rs(11,39-42)", Int (Unsigned, FixedWidthRank (3))))]);
      IntLit (loc "verified/lib.rs(11,49-50)", big_int_of_string "0", false, false, NoLSuffix)
    ]), Sep (loc "verified/lib.rs(12,73-76)", Operation (loc "verified/lib.rs(12,65-67)", Eq, [
      CallExpr (loc "verified/lib.rs(12,5-33)", "object_pointer_within_limits", [], [], [LitPat (Var (loc "verified/lib.rs(12,34-35)", "p")); LitPat (SizeofExpr (loc "verified/lib.rs(12,61-62)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(12,57-60)", Int (Unsigned, FixedWidthRank (3))))))], Static);
      True (loc "verified/lib.rs(12,68-72)")
    ]), Sep (loc "verified/lib.rs(13,59-62)", Operation (loc "verified/lib.rs(13,16-18)", Le, [
      CastExpr (loc "verified/lib.rs(13,7-9)", ManifestTypeExpr (loc "verified/lib.rs(13,10-15)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(13,5-6)", "p"));
      Operation (loc "verified/lib.rs(13,30-31)", Sub, [Operation (loc "verified/lib.rs(13,19-24)", MaxValue (Int (Unsigned, PtrRank)), []); SizeofExpr (loc "verified/lib.rs(13,56-57)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(13,52-55)", Int (Unsigned, FixedWidthRank (3)))))])
    ]), CoefAsn (loc "verified/lib.rs(14,5-6)", VarPat (loc "verified/lib.rs(14,7-8)", "f"), PointsTo (loc "verified/lib.rs(14,13-16)", Deref (loc "verified/lib.rs(14,10-11)", Var (loc "verified/lib.rs(14,11-12)", "p")), "RegularPointsTo", VarPat (loc "verified/lib.rs(14,18-19)", "v")))))))), ("outcome", SwitchExpr (loc "verified/lib.rs(9,42-15,32)", Var (loc "verified/lib.rs(9,42-15,32)", "outcome"), [
      SwitchExprClause (loc "verified/lib.rs(15,13-14)", "returning", ["result"], CoefAsn (loc "verified/lib.rs(15,13-14)", LitPat (Var (loc "verified/lib.rs(15,14-15)", "f")), PointsTo (loc "verified/lib.rs(15,20-23)", Deref (loc "verified/lib.rs(15,17-18)", Var (loc "verified/lib.rs(15,18-19)", "p")), "RegularPointsTo", LitPat (Var (loc "verified/lib.rs(15,24-25)", "v")))));
      SwitchExprClause (loc "verified/lib.rs(9,42-15,32)", "unwinding", [], EmpAsn (loc "verified/lib.rs(9,42-15,32)"))
    ], None)))), false, Some (([
      DeclStmt (loc "verified/lib.rs(9,1-21,2)", [(loc "verified/lib.rs(9,1-21,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(9,42)", StructType ("std_tuple_0_", []))), "$_0", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-21,2)", [(loc "verified/lib.rs(9,1-21,2)", Some (ConstTypeExpr (loc "verified/lib.rs(9,1-21,2)", PtrTypeExpr (loc "verified/lib.rs(16,9-10)", ManifestTypeExpr (loc "verified/lib.rs(16,9-10)", Int (Unsigned, FixedWidthRank (3)))))), "q", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-21,2)", [(loc "verified/lib.rs(9,1-21,2)", Some (ConstTypeExpr (loc "verified/lib.rs(9,1-21,2)", ManifestTypeExpr (loc "verified/lib.rs(17,9-14)", Int (Unsigned, FixedWidthRank (3))))), "first", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-21,2)", [(loc "verified/lib.rs(9,1-21,2)", Some (ConstTypeExpr (loc "verified/lib.rs(9,1-21,2)", ManifestTypeExpr (loc "verified/lib.rs(18,9-15)", Int (Unsigned, FixedWidthRank (3))))), "second", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-21,2)", [(loc "verified/lib.rs(9,1-21,2)", Some (ConstTypeExpr (loc "verified/lib.rs(9,1-21,2)", ManifestTypeExpr (loc "verified/lib.rs(19,9-18)", Bool))), "_observed", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-21,2)", [(loc "verified/lib.rs(9,1-21,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(19,21-26)", Int (Unsigned, FixedWidthRank (3)))), "$_6", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-21,2)", [(loc "verified/lib.rs(9,1-21,2)", Some (ManifestTypeExpr (loc "verified/lib.rs(19,30-36)", Int (Unsigned, FixedWidthRank (3)))), "$_7", None, (ref (false), ref (None)))]);
      DeclStmt (loc "verified/lib.rs(9,1-21,2)", [(loc "verified/lib.rs(9,1-21,2)", Some (ConstTypeExpr (loc "verified/lib.rs(9,1-21,2)", ManifestTypeExpr (loc "verified/lib.rs(20,5-36)", StructType ("std_tuple_0_", [])))), "$_8", None, (ref (false), ref (None)))]);
      LabelStmt (loc "verified/lib.rs(16,9-10)", "0");
      RustStorageLiveStmt (loc "verified/lib.rs(16,9-10)", loc "verified/lib.rs(16,9-10)", "_2", "q");
      ExprStmt (AssignExpr (loc "verified/lib.rs(16,13-14)", Var (loc "verified/lib.rs(16,13-14)", "q"), Initialization, Var (loc "verified/lib.rs(16,13-14)", "p")));
      RustStorageLiveStmt (loc "verified/lib.rs(17,9-14)", loc "verified/lib.rs(17,9-14)", "_3", "first");
      ExprStmt (AssignExpr (loc "verified/lib.rs(17,26-28)", Var (loc "verified/lib.rs(17,26-28)", "first"), Initialization, Deref (loc "verified/lib.rs(17,26-28)", Var (loc "verified/lib.rs(17,26-28)", "p"))));
      RustStorageLiveStmt (loc "verified/lib.rs(18,9-15)", loc "verified/lib.rs(18,9-15)", "_4", "second");
      ExprStmt (AssignExpr (loc "verified/lib.rs(18,27-29)", Var (loc "verified/lib.rs(18,27-29)", "second"), Initialization, Deref (loc "verified/lib.rs(18,27-29)", Var (loc "verified/lib.rs(18,27-29)", "q"))));
      RustStorageLiveStmt (loc "verified/lib.rs(19,9-18)", loc "verified/lib.rs(19,9-18)", "_5", "_observed");
      RustStorageLiveStmt (loc "verified/lib.rs(19,21-26)", loc "verified/lib.rs(19,21-26)", "_6", "$_6");
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,21-26)", Var (loc "verified/lib.rs(19,21-26)", "$_6"), Mutation, Var (loc "verified/lib.rs(19,21-26)", "first")));
      RustStorageLiveStmt (loc "verified/lib.rs(19,30-36)", loc "verified/lib.rs(19,30-36)", "_7", "$_7");
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,30-36)", Var (loc "verified/lib.rs(19,30-36)", "$_7"), Mutation, Var (loc "verified/lib.rs(19,30-36)", "second")));
      ExprStmt (AssignExpr (loc "verified/lib.rs(19,21-36)", Var (loc "verified/lib.rs(19,21-36)", "_observed"), Initialization, Operation (loc "verified/lib.rs(19,21-36)", Eq, [Var (loc "verified/lib.rs(19,21-36)", "$_6"); Var (loc "verified/lib.rs(19,21-36)", "$_7")])));
      RustStorageDeadStmt (loc "verified/lib.rs(19,35-36)", loc "verified/lib.rs(19,35-36)", "_7", "$_7");
      RustStorageDeadStmt (loc "verified/lib.rs(19,35-36)", loc "verified/lib.rs(19,35-36)", "_6", "$_6");
      RustStorageLiveStmt (loc "verified/lib.rs(20,5-36)", loc "verified/lib.rs(20,5-36)", "_8", "$_8");
      PureStmt (loc "verified/lib.rs(20,5-160)", Assert (loc "verified/lib.rs(20,9-15)", Operation (loc "verified/lib.rs(20,71-73)", Or, [
        Operation (loc "verified/lib.rs(20,57-59)", Le, [
          Operation (loc "verified/lib.rs(20,28-29)", Add, [CastExpr (loc "verified/lib.rs(20,19-21)", ManifestTypeExpr (loc "verified/lib.rs(20,22-27)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,17-18)", "p")); SizeofExpr (loc "verified/lib.rs(20,54-55)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(20,50-53)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(20,62-64)", ManifestTypeExpr (loc "verified/lib.rs(20,65-70)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,60-61)", "q"))
        ]);
        Operation (loc "verified/lib.rs(20,114-116)", Le, [
          Operation (loc "verified/lib.rs(20,85-86)", Add, [CastExpr (loc "verified/lib.rs(20,76-78)", ManifestTypeExpr (loc "verified/lib.rs(20,79-84)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,74-75)", "q")); SizeofExpr (loc "verified/lib.rs(20,111-112)", TypeExpr (ManifestTypeExpr (loc "verified/lib.rs(20,107-110)", Int (Unsigned, FixedWidthRank (3)))))]);
          CastExpr (loc "verified/lib.rs(20,119-121)", ManifestTypeExpr (loc "verified/lib.rs(20,122-127)", Int (Unsigned, PtrRank)), Var (loc "verified/lib.rs(20,117-118)", "p"))
        ])
      ])));
      RustStorageDeadStmt (loc "verified/lib.rs(20,36-37)", loc "verified/lib.rs(20,36-37)", "_8", "$_8");
      RustStorageDeadStmt (loc "verified/lib.rs(21,1-2)", loc "verified/lib.rs(21,1-2)", "_5", "_observed");
      RustStorageDeadStmt (loc "verified/lib.rs(21,1-2)", loc "verified/lib.rs(21,1-2)", "_4", "second");
      RustStorageDeadStmt (loc "verified/lib.rs(21,1-2)", loc "verified/lib.rs(21,1-2)", "_3", "first");
      RustStorageDeadStmt (loc "verified/lib.rs(21,1-2)", loc "verified/lib.rs(21,1-2)", "_2", "q");
      ReturnStmt (loc "verified/lib.rs(21,2)", Some (CallExpr (loc "verified/lib.rs(21,2)", "returning", [], [], [LitPat (Var (loc "verified/lib.rs(21,2)", "$_0"))], Static)))
    ], loc "verified/lib.rs(21,1-2)")), false, [])
  ])
]