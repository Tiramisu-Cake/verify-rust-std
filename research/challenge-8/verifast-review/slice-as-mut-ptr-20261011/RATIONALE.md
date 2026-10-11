# Slice as_mut_ptr binding integration — before implementation

Session I begins2026-10-11T16:16:32Z; main18:16:32Z; finish-only18:46:32Z, Cloud ceiling3600seconds ownerverifast, newaccount. Base Hcheckpoint6b2d03d0/tool46181, incoming64922e1 exactpatch f200a581. Independent addressed semantic review requested before tool delta.

Proposed scope: add exact compiler symbol std::slice::<impl [T]>::as_mut_ptr to existing as_ptr typed-cast lowering. Preserve its exact substitutions/one receiver handling; no unknownmethod fallback, memory model, permissions, initialized-T, lifetime/aliasing fact added. Source applicability pinned slice/mod.rs method body self as *mut [T] as *mut T. Translator symbol/type guards and runner source/MIR/refinement checks must be documented separately: source hashes are runner admission, not translator enforcement.

Cloud before compilation must materialize full30 modules/twoXZ, import dependencies and prepare pointer/native/Bool fixtures. New tool must freshly verify generic/MU components, isolatedconsumer, wrongpointer/missingrawrights/MU initialized negatives and exact sourcecontrols; nativeC1/C4, ninebodyselector and former C4+firstselect composition compatibility. Retain C/C++ -shared for any rerun. Unaffected gates reuse requires recorded meaningful-input argument, not wholetoolhashupdate.

Caller len+16 failure, publicZSTguard and transfer, nativeC4+select/fullsort4 remain first-agentmission. No supplied premises or lowered contracts. Kernel/ZST/specs/CURRENT/nativeC3isolation and outerFpositive preserved. OldHREADY and all historical verdicts remain pinned; separatecandidate only.
