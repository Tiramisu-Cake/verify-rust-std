# R24 compile-scope correction

Build0b240663 console-build exit2 is reported by exact Brief log1091-1095:
the early new admission module references `TranslatorArgs` at1124, while that
alias is declared later at2717. The enclosing `Make (Args : VF_MIR_TRANSLATOR_ARGS)`
starts at340 and exposes the identical `ignore_unwind_paths : bool` field.
Replace only this one reference with `Args.ignore_unwind_paths` in a separate
overlay after row29. Keep the failed patch and Build pins immutable.

This is a same-boundary compilation correction. It preserves the exact
rejection of ignore-unwind paths, all prior gates, source/MIR admission,
projection shape/counts, ordinary same-unit body checking, and all normal/
unwind/abort/Drop/leak/refinement/ownership/thread/provenance controls. No
classifier or target pins change. Entry/fingerprint/baseline AST flag scope
is unchanged. Skipping the guard or moving a different scope into it was
rejected because the existing functor argument already supplies the right value.

Runner applies both exact hash-pinned overlays in order and checks intermediate
and final translator hashes plus unchanged final four-file inventory. Actual
profile metadata records the new final translator hash. Static patch
reproduction and shell/Python parse checks precede delta review; compilation
and proof are authorized only in the next full1200 Cloud Build. No local compiler.
