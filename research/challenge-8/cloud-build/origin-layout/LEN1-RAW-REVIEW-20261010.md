# Independent raw canonical interface review — c6e247a9

Exact proof=infra20548c2798115ba6f1ac0d7632aeddc11ea0e8a3/tool df6b3fbf/profile0b8cf55b;
archiveed26546a6d4efbdd4f850b6ed5cb9fa6de18f34d8d27424853d9887d7466c5c3 integrity verified.
Independent reviewer /root/review_bridge inspected actual source, parsed AST,
MIR and verifier traces. Raw direct and canonical positives: all4 stages0,
actualbodycopy, normal return, leak check and0errors. This is individual raw
proof evidence, not acceptance of the complete campaign or arbitrary effect AST.

Canonical_positive has nonempty own: type_interp, len1, sourcequarter atCURRENT,
destination uninit, u64own and source/destination separation. Generated FBC
contains src/dst/len fields, padding and own for their saved value. Safety proof
opens FBC+own, creates exact singleton array views without losing quarter/full
coefficients, calls checked body at104, closes same-file effect at105. Trace
confirms Verifying call, effectchunk production, prototype compatibility leak
check; actualruntime bodycopy111/return113/leak/0errors. Defined effect AST
has len==1, type_interp, quarter source singletonCURRENT, full destination
singleton sameCURRENT and u64own. Generated normal posts contain fields/padding
and exactly effect; unwind fields/padding arm omits effect unchanged.

Conditional interface fragment only. Generated pre ref_origin(self)==self,
fullFBC, thread/lifetime resources and own must be obtained from an actual
caller. Own's explicit len1/payload geometry/separation are not caller-derived
here. Source body is mechanically u64-specialized actual same-version code,
not compiler-generated monomorphic MIR or actual Drop terminator/glue. No
user-authored Assume/Leak in checked proof/effect; preexisting generated
end_ref_padding false-assumption stub is outside the trace and not called.
No global claim that all AST assumptions are absent.

No-effect control has sole intended prototype residual payload leak:
verified/lib.rs(42,5-105,6) type_interp<u64>(), [1/4]array<u64>(src,1,cons(current0,nil)),
array<u64>(dst,1,cons(current0,nil)); follows checked call97/leak check.
Missingquarter/gap and malformedsignature/missingdefinition reach respective
resource/qualification failures. Full structured admission still pending
classifier binding, not bypassed by this review.

Duplicateeffectclose unexpectedlypasses: firstclose105 produces effect, second
close106 Auto-opening predicate atdefinition42, consumes samepayload/typeinterp
and refolds. This does not require two simultaneous full effects. It is a bad
negative oracle, not demonstrated resource duplication. Keep unexpectedresult,
all_matchedfalse/originalaggregateINCONCLUSIVE. Future simultaneous-effect
negative needs fresh source/proof; no newexperiment after main in thissession.
