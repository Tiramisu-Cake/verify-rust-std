"""Static generator: additive mutable translation branches against frozen C8."""
from pathlib import Path
import re,hashlib
BASE_SHA='c8f5ce1da4f88a4b029b8ed12cc7667a0e227836b1843a1590f78769e073201e'
MODULES=['MaybeUninit','AsMutPtr','PointerDrop','G1Call','GenericGuard','ActualNestedH2','ActualForgetOwn','SelectIntrinsic','A1Link','A1Nine','R24CheckedPointerOutcomes']
def mut(text):
 for name in MODULES:text=text.replace('Sort4'+name,'Sort4Mut'+name)
 return text.replace('*const Element','*mut Element')
def generate(base):
 assert hashlib.sha256(base.encode()).hexdigest()==BASE_SHA
 lines=base.splitlines(True);edits=[]
 def text(lo,hi):return ''.join(lines[lo-1:hi])
 def edit(lo,hi,new):edits.append((lo-1,hi,new))
 def parallel_expr(lo,hi):
  old=text(lo,hi);clone=mut(old)
  # Caller range begins at if and ends before its trailing else fallback.
  assert old.lstrip().startswith('if ')
  indent=old[:len(old)-len(old.lstrip())]
  edit(lo,hi,clone+'\n'+indent+'else '+old.lstrip())
 # Guarded call arms: keep each original const branch byte for byte.
 arms=[(3293,3329),(3330,3364),(3558,3589),(3590,3618),(3619,3647),(3648,3681),(3682,3718),(3719,3735),(3736,3774),(3775,3784),(3841,3876)]
 for lo,hi in arms:edit(lo,hi,mut(text(lo,hi))+text(lo,hi))
 # Local-union remap, pointer-value ownership and aggregate representation.
 parallel_expr(1574,1580)
 old=text(1618,1623)
 edit(1618,1623,'('+mut(old.strip())+') ||\n'+old)
 old=text(4640,4655)
 clone=mut(old).replace('if adt_kind = Mir.Union', 'if !Sort4MutMaybeUninit.active && adt_kind = Mir.Union',1)
 edit(4640,4655,clone+'\n          else '+old.lstrip())
 # The local union name is shared, so the mutable aggregate arm must be gated.
 old=text(4697,4722)
 assert old.lstrip().startswith('| AggKindCertifiedMaybeUninit')
 clone=mut(old).replace('| AggKindCertifiedMaybeUninit ptr_ty ->','| AggKindCertifiedMaybeUninit ptr_ty when !Sort4MutMaybeUninit.active ->',1)
 edit(4697,4722,clone+old)
 # Checked no-unwind projections from local same-unit proved callees.
 mut_owner=mut(text(3953,4006)).replace('checked_owner_no_unwind','checked_mut_owner_no_unwind')
 mut_outcome=mut(text(4007,4070)).replace('checked_r24_pointer_outcome','checked_mut_r24_pointer_outcome')
 edit(4071,4070,mut_owner+mut_outcome) # insertion before following result projection
 old=text(4072,4073)
 edit(4072,4073,old.replace('checked_r24_pointer_outcome then','checked_r24_pointer_outcome || checked_mut_owner_no_unwind ||\n           checked_mut_r24_pointer_outcome then'))
 # Fractional ghost builtin CFG consistency for the independently certified family.
 for line in (4230,4249):
  old=text(line,line);assert 'actual_fractional_variant' in old
  edit(line,line,old.replace('!Sort4SelectIntrinsic.actual_fractional_variant <> None','(!Sort4SelectIntrinsic.actual_fractional_variant <> None ||\n                       !Sort4MutSelectIntrinsic.actual_fractional_variant <> None)'))
 # Nested guard field projection and ghost scopes retain original checks.
 parallel_expr(6172,6185)
 parallel_expr(6553,6572)
 # Suppress only the exact certified representation ADT, separately for each family.
 old=text(7969,7969)
 edit(7969,7969,old.rstrip()+' ||\n       (!Sort4MutMaybeUninit.active && def_path = Sort4MutMaybeUninit.union_name)\n')
 # Admission is after legacy resets and before any header/type/body translation.
 old=text(14124,14124);assert 'Sort4R24CheckedPointerOutcomes.admit' in old
 edit(14124,14124,old+'      let* () = certify_sort4_mutable_bundle vf_mir_cpn in\n')
 # All nine bodies must survive ordinary filtering; expected call counts separate.
 checks=mut(text(14313,14337)).replace('expected_redirects','expected_mut_redirects').replace('expected_as_mut_ptr_redirects','expected_mut_as_mut_ptr_redirects').replace('expected_sort4_redirects','expected_sort4_mut_redirects').replace('expected_sort4_as_mut_ptr_redirects','expected_sort4_mut_as_mut_ptr_redirects')
 checks+='      let* () = check_sort4_mutable_body_inventory bodies_cpn in\n'
 edit(14338,14337,checks)
 counters=mut(text(14353,14431)).replace('expected_redirects','expected_mut_redirects').replace('expected_as_mut_ptr_redirects','expected_mut_as_mut_ptr_redirects')
 counters+='      if !Sort4MutR24CheckedPointerOutcomes.active then\n        Printf.printf "SORT4-R24-MUTABLE-CERTIFICATES: case=%s bodies=9 pointer_drop=1 assume_init=1; raw MIR cleanup retained\\n%!"\n          (Sort4MutableProfile.case_name ());\n'
 edit(14432,14431,counters)
 for lo,hi,new in sorted(edits,reverse=True):lines[lo:hi]=[new]
 return ''.join(lines)
if __name__=='__main__':
 import sys
 Path(sys.argv[2]).write_text(generate(Path(sys.argv[1]).read_text()))
