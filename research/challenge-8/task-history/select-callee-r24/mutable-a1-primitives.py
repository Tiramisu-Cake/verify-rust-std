#!/usr/bin/env python3
"""Generate an additive mutable A1 primitive overlay over the compiled eca unit."""
from pathlib import Path
import hashlib,difflib
BASE_SHA='eca440a605ab3900c39d9e58328b487104a1b33f75d90323036f6beab09aa162'
HERE=Path(__file__).resolve().parent

def generate(base):
    assert hashlib.sha256(base.encode()).hexdigest()==BASE_SHA
    def insert(anchor,addition):
        nonlocal base
        assert base.count(anchor)==1,anchor
        base=base.replace(anchor,addition+anchor,1)
    insert('  module CapnpAux = struct\n','''  module Sort4MutableA1Primitives = struct
    let inhabited_count = ref 0
    let transmute_count = ref 0
    let reject why = failwith ("SORT4-R24-MUTABLE-A1-PRIMITIVES: refusal: " ^ why)
  end

''')
    insert('            | "std::intrinsics::assert_inhabited" -> (\n','''            | "std::intrinsics::assert_inhabited"
              when !Sort4MutA1Nine.active &&
                   !Sort4MutR24CheckedPointerOutcomes.active &&
                   State.body_name = Sort4MutA1Link.caller_name ->
                (match fn_def_ty_cpn.substs, substs_cpn, args_cpn with
                 | [{kind=Type p}], [{kind=Type q}], []
                   when fn_def_ty_cpn.late_bound_generic_param_count = 0 &&
                        p = q && Sort4MutA1Link.const_ptr p ->
                     incr Sort4MutableA1Primitives.inhabited_count;
                     if !Sort4MutableA1Primitives.inhabited_count <> 1 then
                       Sort4MutableA1Primitives.reject "assert_inhabited count";
                     (* A raw pointer value is inhabited for unrestricted Element;
                        no pointee ownership or Drop premise is introduced. The
                        exact local graph retains the nounwind intrinsic edge. *)
                     Ok (tmp_rvalue_binders, FnCallResult (mk_unit_expr fn_loc))
                 | _ -> Sort4MutableA1Primitives.reject
                     "exact mutable assert_inhabited type/body/substitutions")
''')
    start=base.index('          | { kind = Transmute;\n',base.index('          match cast_data with\n'))
    end=base.index('          | {operand=Copy {local; projection=[BoxAsNonNull _]}} ->\n',start)
    original=base[start:end]
    mutable=original.replace('mutability = Not','mutability = Mut')
    mutable=mutable.replace('ty = ({ kind = Param _ } as elem_ty)','ty = ({ kind = Param "Element" } as elem_ty)')
    mutable=mutable.replace('when (match List.assoc_opt source_local Args.local_decl_types with',
      'when !Sort4MutA1Nine.active &&\n                   !Sort4MutR24CheckedPointerOutcomes.active &&\n                   State.body_name = Sort4MutA1Link.callee_name &&\n                   source_local = "_3" &&\n                   (match List.assoc_opt source_local Args.local_decl_types with')
    mutable=mutable.replace('including const mutability','including mutable pointer kind')
    mutable=mutable.replace('            (match operand with','''            incr Sort4MutableA1Primitives.transmute_count;
            if !Sort4MutableA1Primitives.transmute_count <> 1 then
              Sort4MutableA1Primitives.reject "transmute count";
            (match operand with''',1)
    base=base[:start]+mutable+base[start:]
    # Fail closed for any other mutable-pointer Transmute in this exact profile.
    anchor='''          | { kind = Transmute;
              ty = { kind = RawPtr {
                ty = { kind = Param _ }; mutability = Not } } } ->
'''
    insert('          | {operand=Copy {local; projection=[BoxAsNonNull _]}} ->\n','''          | { kind = Transmute; ty = { kind = RawPtr {mutability = Mut; _} } }
              when !Sort4MutA1Nine.active ->
            Error (`TrRvalue
              "uncertified mutable-pointer transmute source, body, or operand")
''')
    insert('    Sort4MutableProfile.root := None;\n','''    Sort4MutableA1Primitives.inhabited_count := 0;
    Sort4MutableA1Primitives.transmute_count := 0;
''')
    marker='''      if !Sort4MutR24CheckedPointerOutcomes.active then
        Printf.printf "SORT4-R24-MUTABLE-CERTIFICATES: case=%s bodies=9 pointer_drop=1 assume_init=1; raw MIR cleanup retained\\n%!"
          (Sort4MutableProfile.case_name ());
'''
    assert base.count(marker)==1
    base=base.replace(marker,'''      if !Sort4MutR24CheckedPointerOutcomes.active then (
        if !Sort4MutableA1Primitives.inhabited_count <> 1 ||
           !Sort4MutableA1Primitives.transmute_count <> 1 then
          Sort4MutableA1Primitives.reject "exactly one inherited mutable primitive at each A1 site";
        Printf.printf "SORT4-R24-MUTABLE-A1-PRIMITIVES: assert_inhabited=1 transmute=1\\n%!";
        Printf.printf "SORT4-R24-MUTABLE-CERTIFICATES: case=%s bodies=9 pointer_drop=1 assume_init=1; raw MIR cleanup retained\\n%!"
          (Sort4MutableProfile.case_name ()));
''',1)
    return base

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--base',type=Path,default=Path('/tmp/r24-translator-mut.ml'));parser.add_argument('--check',action='store_true');args=parser.parse_args()
    base=args.base.read_text();final=generate(base)
    patch=''.join(difflib.unified_diff(base.splitlines(True),final.splitlines(True),fromfile='a/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml',tofile='b/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'))
    target=HERE/'mutable-a1-primitives-r24.patch'
    if args.check:assert target.read_text()==patch
    else:target.write_text(patch)
    Path('/tmp/r24-translator-mut-a1.ml').write_text(final)
    print('patch',hashlib.sha256(patch.encode()).hexdigest(),'translator',hashlib.sha256(final.encode()).hexdigest())
if __name__=='__main__':main()
