# R17 S4: checked callback equalities in ghost context

S3 Cloud built the new translator and ran actual-body verification; Brief records `Cannot read a ghost variable in a non-pure context` at actual c1 source line245. The newly injected receiver/tuple equalities are proof assertions, but were emitted as bare Ast.Assert statements while referring to ghost precreated refs.

Apply only to the three new checked callback binding assertions: wrap each existing Ast.Assert in Ast.PureStmt at the identical call location. Preserve each equality expression, actual receiver/tuple locals, ghost reference identity, order and call-index/source guards. This selects the intended ghost proof context; it neither assumes the equality nor produces ownership. The same kernel must prove all assertions. Runtime/CFG/contracts/normal/unwind/current-owner resource flow unchanged. Source-specific controls and Cloud proof remain required; compilation or partial progress does not establish proof credit.
