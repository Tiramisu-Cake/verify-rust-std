# Lookup controls: specified, NOT_RUN

STOP dependency: REQUIRED-STATE.md. No compiler resolver, unit tests or fault injection were added.
TEST-MANIFEST.json enumerates the required scenarios as specifications; it is not test evidence.

When the fact is REQUIRED, distinguish zero markers, one marker/no emitted symbol, multiple
markers and ambiguous symbol binding. Preserve one whole-static Lambda plus the existing user
targets when lookup succeeds. The success path must remain present with uninit disabled too.
NOT_REQUIRED and uninit-off absence must not introduce the new missing-state diagnostic.
UNKNOWN must not be mapped to NOT_REQUIRED or treated as established REQUIRED.

The pure resolver must accept synthetic candidate sets, so absent/ambiguous cases do not need
a broken runtime, a CLI injection switch, public marker suppression or trusted skips.
Its test does not establish source→emitted binding. Three normal integrations remain necessary:
uninit-off PFC, uninit-on/no writes inside the wrapper, and normal uninit-on private writes.
Reset may make the state emitted even in the no-wrapper-writes control; that is expected.

## Rust API and type audit (read-only)

- `handle_check_contract` receives `InternalDefId` and `&[MonoItem]`, resolves `Instance`,
  and returns `AssignsContract`; it currently has no Result/error return.
- `find_modifies` reads `VarDebugInfoContents`, obtains `TyKind::RigidTy(RigidTy::Closure(..))`,
  and resolves a closure `Instance`. This binds the wrapper, not its transitive effects.
- `func.ty(body.locals())` returns a Result containing `Ty`; `resolve_call` takes that Ty,
  requires FnDef and returns `Result<Instance, String>`. FnPtr is not a resolved callee.
- `fn_marker(StaticDef)` returns `Option<String>`; `Instance::from(StaticDef).mangled_name()`
  supplies a String accepted by `SymbolTable::lookup<T: Into<InternedString>>`.
- `lookup` returns `Option<&Symbol>`; current `.cloned().map(...)` constructs one
  `Vec<Lambda>` using `Lambda::as_contract_for(..., symbol.to_expr())`.
- `SymbolTable` is a `BTreeMap<InternedString, Symbol>`; insertion asserts uniqueness
  (`cprover_bindings/src/goto_program/symbol_table.rs:11,53`). Two entries at one key cannot
  be recovered as a late resolver ambiguity. A synthetic ambiguity case must describe
  candidate-to-symbol binding, not invent a multimap API or promise to replace insertion ICEs.
- Existing `tcx.dcx().fatal(...)` model errors occur in immutable allocation finalization;
  `tcx.dcx().struct_span_err(...).with_note(...).emit()` is used in the contract transform.
  A future diagnostic must name contract/context and marker/symbol lookup stage through that API.
  No new production import, operand construction or error-flow path was implemented/typechecked.

No panic/ICE replacement or failure classification is claimed. The current `.find()` and
`.unwrap_or_default()` remain unchanged while required-state is unresolved.
