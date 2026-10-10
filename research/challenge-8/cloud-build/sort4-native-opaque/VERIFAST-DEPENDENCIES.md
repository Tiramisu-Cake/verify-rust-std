# Native opaque transition: reproducible dependency boundaries

Tool HEAD f76012fb518703b1d98e243ac4f487f16877cfcb alone does not identify
the effective profile. Frozen C4 translator is
1eab6eb54fe5c23d53ca72a6d9dfcbbff09c09ffaf26c48a4f450f5068a8d313;
kernel37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c.
See FROZEN-C4-SNAPSHOT.json in ../sort4-native-c4 and FRESH-D776-REVIEW.md
for the remaining effective hashes, exact fresh artifacts and commands.

## Strict comparison entry

Fresh d77612a5 on86e38e3a translated the safe native C1 candidate, entered
its body, derived source4/tail resources from its native reference and kept
MU scratch/F/thread resources. At source172:1–30, `let_lft 'cmp`, VF refuses:
`Strict lifetime binding has unresolved inference in entry outer type`.
The callback at210:21–92 and normal/direct-unwind posts are not reached.
Kernel freeze_strict_type2545 rejects unresolved InferredType while checking
all outer types at2585–2595. This is a setup refusal, not a semantic negative.

The actual input reference types come from D.inputs. MIR also has outer
temporaries with erased reference lifetimes: `_5: &'erased [T]` from v.len(),
and callback `_55: &mut F`, `_56: (&T,&T)`, `_57`–`_62` shared references.
Naming native parameters does not establish that all these outer temporary
types have inferred lifetimes. Exact culprit attribution needs fresh pre-AST
capture. A callback-free prepared-resource component is a separate diagnostic;
its result must not be substituted for the actual call.

Potential required rule if narrow binding cannot resolve it: infer or bind the lifetime/type of real MIR reference
temporaries sufficiently to pass strict entry while retaining strict heap,
outer-type and bound escape checks on normal/return/unwind/outgoing-goto,
and allocation/free, token, owner and debt conservation. No rule is changed
here. Erasing the cut, replacing it with Noop, or dropping local resources
would not close this dependency.

## Checked usize arithmetic and panic

Minimal source is `fn small_sort_general_with_scratch(len: usize) { let _need
= len + 16; }`, source SHA601fe289c804513c48dd5a432a083920fd2f9bd6f3d6fa1be1b7850961dc5283.
Pinned rustc with --emit=mir -Coverflow-checks=on -Cpanic=unwind
-Copt-level=0 -Zmir-opt-level=0 emits AddWithOverflow and Assert(!overflow),
with success and unwind continue. Checked MIR SHA
b529e8c4d717a76f883833f75abd8b241bc5fc0eb9f133039011ef247512c48a.

Frozen exporter lib.rs69 appends -Coverflow_checks=off after user arguments;
--no-default-args does not remove it. Its paired exported MIR instead contains
ordinary add and no Assert (SHAa917ed828acb3b28ef766a6ba38e1afc7d9627cc2bdc967172a68797b1aac9a4).
VF then stops at3:17–25 on potential arithmetic overflow. The actual checked
panic route is absent from this proof pipeline, not proved unsafe at runtime.
Required upstream work: preserve explicit overflow-check configuration and
support checked operation plus Assert/unwind without assuming an arbitrary
len bound or discarding panic. No exporter/arithmetic semantics changed here.

## External pointer method edge

Fresh d776 pointer-expression VF0/90 proves source-linked slice-to-thin-pointer
casts, native source4 permissions and full native normal posts with opaque MU
scratch. This is an implementation-expression component. Actual external
as_mut_ptr method-call binding remains absent; it needs a proved actual callee
and compatible call summary. Numeric pointer equality creates no ownership.

No MaybeUninit inverse or optional-T destination adapter is required for the
opaque prefix interface. Native→actual C1/C4 and the full external caller
remain unproved. Positive T size is an explicit bounded comparison condition,
not a consequence of the selected native branch: len8,size0 is a counterexample.

## Conditional narrow binding path, not a general-rule conclusion

Independent review21:03UTC: if callback-free preparation passes strict entry
and native-only pre-AST capture succeeds, an exact C1 binding patterned on C4
may suffice without a new general rule. This remains conditional. Old C4
admission/relocation/indices/FnMut rewrite are sort4_stable-specific, not a
native summary. The native marker includes an extra full-native cleanup block
for scratch MU/F/thread/type posts after debt/recover/four-cell join. Its
allocation/free and every direct-unwind resource must remain present. Native
local inventories and compiler-derived lifetime/Output=bool registration need
fresh exact source/MIR/pre-AST pins and independent address review before any
binding implementation. Failure of callback-free preparation instead isolates
an earlier dependency; the first failure must be recorded without upgrading
later target posts. Neither decision accepts a general strict-cut draft.
