# Cache invariant — T1b-P
Unit sharing is valid only for pristine, root-independent local transformations under identical unit/stubs/config, with matching auxiliary metadata.
Global-pass results, root reachability/call graphs and bodies consumed by GOTO emission must be root-scoped.
The prototype shares no body cache: ordering uses a disposable unit-configured transformer; every root creates a fresh transformer with the same constructor inputs.
Each root owns stub/inst pass objects, cache, generated_loop_modifies and loop_modifies_bindings through complete synchronous GOTO body emission.
The export worker receives owned symbol/type/vtable data, never a transformer reference; no transformer is needed for later serialization.
GlobalPasses remain cloned from the same template per root; local pass order, CheckRef, ordinary/constant transfer, library, flags and ordering algorithm remain unchanged.
Diagnostic body_hashes/last_writers stay unit-scoped observers and are never consulted by transformations; a stale label is not body provenance.
This is an uncompiled causal prototype, not a production fix or proof; a pristine local cache plus root overlay is deferred.
