# KANI3300 G1R — static compilation sweep
Paths: C/=kani-compiler/src/kani_middle/transform/check_uninit/, L/=library/kani_core/src/. Scope: entire production diff `657c2b24516b967f67ce71994299d0ef328aede9..3d085249c9c6c49a9c2e5747e2167d629748fb70` (five files).
References: Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`; exact nightly-2026-10-23 source `7189d39d9ce936881b8132c6addeaf3e295cd455` (API-SOURCES.json).
- C/ptr_uninit/uninit_visitor.rs:51 → MirVisitor::visit_operand/super_operand take &Operand, Location; Place cloned, collector owns Vec<Place>; visit_rvalue takes &Rvalue.
- C/ptr_uninit/uninit_visitor.rs:79 → MutableBody::locals returns &[LocalDecl], arg_count usize; local.ty is Copy Ty; collected references borrow body, not visitor.
- C/ptr_uninit/uninit_visitor.rs:138 → union_storage(TyCtxt, Ty)->bool; PointeeInfo::from_ty returns Result; union_as_field_error returns owned Option<LayoutComputationError>.
- C/ptr_uninit/uninit_visitor.rs:156 → Ty::kind returns owned TyKind; RawPtr/Ref contain Copy Ty, pointer kind predicates return bool.
- C/ptr_uninit/uninit_visitor.rs:167 → Operand::ty/Place::ty return Result<Ty, Error>; ok/map/is_ok_and closures receive Ty by value; no borrowed value escapes.
- C/ptr_uninit/uninit_visitor.rs:178 → collector.visit_rvalue signature matches; owned places consumed after traversal, Copy(place) moves an owned Place.
- C/ptr_uninit/uninit_visitor.rs:214 → Result::is_ok_and and Option::is_some signatures match; no move from borrowed projection.
- C/ptr_uninit/uninit_visitor.rs:259 → AggregateKind::Adt union field is &usize in borrowed Rvalue; *field supplies FieldIdx=usize.
- C/ptr_uninit/uninit_visitor.rs:304 → TyConst::eval_target_usize returns Result<u64, Error>; ConstantIndex.offset/min_length are u64; Vec lengths remain usize.
- C/ptr_uninit/uninit_visitor.rs:321 → FIX: shape().size is MachineSize; .bytes(self)->usize supplies vec![false; source_size].
- C/ptr_uninit/uninit_visitor.rs:431 → Place clones precede mutation; projection traversal borrows MIR place, not self; new CheckRef operands own their places.
- C/ptr_uninit/uninit_visitor.rs:519 → updated assign_storage/visit_ordinary_assignment signatures include Location at every call; before/after operations retain matching enum payloads.
- C/ptr_uninit/uninit_visitor.rs:578 → Instance::name returns Symbol=String; intrinsic_name Option<String>, as_deref Option<&str>; kind Copy InstanceKind; has_body/is_foreign_item bool.
- C/ptr_uninit/uninit_visitor.rs:614 → FIX: Ty::layout()->Result<Layout, Error>, Layout::shape(self)->LayoutShape, size.bytes()->usize for Forget mask.
- C/ptr_uninit/uninit_visitor.rs:628 → String::as_str and intrinsic enum guards have matching types; iterating borrowed args preserves later use; no move from args.
- C/ptr_uninit/uninit_visitor.rs:731 → shadow_pointer/union_pointer take &Operand; TypedSwap/volatile variants exist in pinned Intrinsic; exhaustive fallback remains.
- C/ptr_uninit/uninit_visitor.rs:857 → borrowed RigidTy match uses Copy Ty; Drop/Return, StatementKind, ProjectionElem, Rvalue and InstanceKind matches remain exhaustive (explicit or fallback).
- C/ptr_uninit/uninit_visitor.rs:990 → AddressOf/Ref and Cast patterns match pinned MIR types; borrowed operand/target stay borrowed; no new unchecked conversion.
- C/ty_layout.rs:130 → for_storage returns Result<Self, LayoutComputationError>; validation/data_bytes use ? with same error type; size.bytes is usize.
- C/ty_layout.rs:168 → shape is owned; size read before moving fields; FieldsShape::Union count is NonZero<usize>; Arbitrary has offsets: Vec<MachineSize> only.
- C/ty_layout.rs:175 → offset.bytes()->usize; checked_add(usize)->Option<usize>, is_none_or consumes usize; collect infers Vec<usize>; bounds use usize throughout.
- C/ty_layout.rs:232 → transfer_mask borrows self, returns Vec<bool>; zip yields (&mut bool, &bool); explicit dereferences preserve ownership and bool bit operations.
- C/ty_layout.rs:263 → TyKind::rigid()->Option<&RigidTy>; variants_iter yields VariantDef, fields Vec<FieldDef>, ty_with_args(&GenericArgs)->Ty; args already borrowed.
- C/ty_layout.rs:277 → VariantsShape/TagEncoding shapes match; Array/Slice/Pat bind &Ty, Tuple iterates &Ty; unsupported RigidTy variants exist, fallback exhaustive.
- C/ty_layout.rs:465 → data_bytes_for_ty takes current_offset:usize and returns Result<Vec<DataBytes>, LayoutComputationError>; append receives &mut Vec, ? matches.
- C/mod.rs:165 → union_storage accepts operand.ty(...).unwrap():Ty; layout dispatch branches all return Result<PointeeInfo, LayoutComputationError> or return ().
- C/mod.rs:563 → CreateUnion field &FieldIdx indexes Vec via *field:usize; SetStorage borrows/clones Vec<bool>; byte-mask slice bounds/lengths are usize.
- C/mod.rs:597 → Vec<bool>::iter_mut zipped with owned Vec<bool> yields (&mut bool,bool); &= accepts bool; mk_layout_operand takes &[bool].
- C/mod.rs:693 → MIR StoreArgument args (*const T,usize,bool); LoadArgument args (*const T,usize,[bool;L]); MirConst::try_from_uint(u128,UintTy)->Result, from_bool(bool)->MirConst.
- C/mod.rs:755 → CopyInitStateSingle args (*const T,*const T,[bool;L],bool); matching &operation borrows; constant construction and terminator fields match pinned API.
- C/mod.rs:875 → resolve_mem_init_fn supplies generics [Const(L:usize via u64),Type(T)] in that order to all three models; mk_layout_operand builds [bool;L], unit return local unchanged.
- C/relevant_instruction.rs:217 → removed union_field has no remaining callers; FieldIdx import still used by CreateUnion; all MemoryInitOp matches cover the unchanged variants.
- L/mem_init.rs:45 → argument_buffer_moved:bool initialized in the sole struct constructor; every new local/argument/import is used; no new dead private compiler helper.
- L/mem_init.rs:115 → retain<const L:usize>(&mut self,*const u8,Layout<L>); clear_moved_source::<L> uses four usize IDs/offsets; pointer_object/offset return usize at f046.
- L/mem_init.rs:437 → all models retain <const L:usize,T> (T:Sized); copy_init_state::<L,T> explicit; retain infers L from [bool;L]; clear_moved_source explicit L; pointer casts thin for Sized T.
- L/mem_init.rs:464 → store/load pointer raw-parts APIs already present at f046; bool copied before mutation; shared MEM_INIT_STATE accesses stay in existing unsafe blocks; marker visibility unchanged.
Static result: only the two MachineSize/usize defects found and repaired; no additional source-level signature, borrow, visibility, exhaustive-match or unused-binding issue identified. This is not a -D warnings/compiler PASS. Validation: allowed rustfmt wrapper + git diff --check; cargo/rustc/Kani/CBMC/native NOT_RUN, proof credit NONE, Cloud $0.
