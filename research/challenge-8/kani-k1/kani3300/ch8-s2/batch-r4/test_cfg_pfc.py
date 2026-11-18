# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""R4 distinguishing source mutations; no native compiler/verifier."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import cfg_pfc as c
import ordinary_contracts as o
import s2_correspondence as correspondence
import check_package as cp
import runner

HERE = Path(__file__).resolve().parent
BATCH = correspondence.BATCH
HELPER = c.BASE + 'slice/sort/shared/smallsort/verify/helper_contracts.rs'
PFC = '#[kani::proof_for_contract(sort8_stable)]'


class CfgPfcTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = json.loads((HERE/'S2-SOURCE.json').read_text())
        for rel, text in self.sources.items():
            path = self.root/rel; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text)
        self.request = copy.deepcopy(runner.load_request())
        # Resealed semantic mutations test gates independently of frozen hashes.
        for key in ('cfg_pfc_source_sha256','ordinary_contract_source_sha256'):
            self.request.pop(key)

    def replace(self, rel, old, new):
        p=self.root/rel; self.assertIn(old,p.read_text());p.write_text(p.read_text().replace(old,new))

    def check(self): return c.check(self.root,self.request)

    def test_all_eleven_rows_full_targets_and_uncontracted_ordinary(self):
        doc=self.check(); self.assertEqual(len(doc['rows']),11)
        self.assertEqual(sum(len(r['stub_verified']) for r in doc['rows']),6)
        expected={'sort13_assumed':['swap_if_less'],'general32_assumed':['sort8_stable','insert_tail','bidirectional_merge'], 'general32_weak':['sort8_stable','insert_tail']}
        for row in doc['rows']:
            self.assertEqual([r['target'].split('::')[-1] for r in row['stub_verified']],expected.get(row['id'],[]))
            self.assertTrue(all(r['matching_pfc'] for r in row['stub_verified']))
        ordinary=o.check(self.root,self.request)
        self.assertEqual(len(ordinary['contexts']),11)
        self.assertEqual(len(ordinary['source_files_sha256']),23)
        self.assertEqual(len(ordinary['checked_active_ordinary_uses']),23)
        self.assertTrue(all(not r['active_contract_attrs'] for r in ordinary['checked_active_ordinary_uses']))
        self.assertTrue(any(r['scope']=='CONSERVATIVE_OPAQUE_ALL_ARMS' for r in ordinary['checked_active_ordinary_uses']))
        self.assertFalse(doc['qualification_from_registration'])

    def test_frozen_r3_rejected_at_all_four_bindings(self):
        old=(HERE/'fixtures/s2-r3-batch.rs.txt').read_text()
        self.assertEqual(hashlib.sha256(old.encode()).hexdigest(),correspondence.R3)
        (self.root/BATCH).write_text(old)
        with self.assertRaises(c.GateError) as raised:self.check()
        errors=str(raised.exception).splitlines();self.assertEqual(len(errors),4)
        self.assertEqual(sum('::sort8_stable has active contract attrs' in e for e in errors),2)
        self.assertTrue(any('::swap_if_less has active contract attrs' in e for e in errors))
        self.assertTrue(any('::bidirectional_merge has active contract attrs' in e for e in errors))

    def test_old97ac_still_fails(self):
        (self.root/BATCH).write_bytes((HERE/'fixtures/s2-old97ac-batch.rs.txt').read_bytes())
        with self.assertRaisesRegex(c.GateError,'active contract attrs'):self.check()

    def test_missing_wrong_cfg_cfg_attr_and_disabled_pfc(self):
        cases=['#[kani::proof]', '#[cfg(not(kani_smallsort_s2_assumed))]\n'+PFC,
               '#[cfg_attr(not(kani_smallsort_s2_assumed),kani::proof_for_contract(sort8_stable))]',
               '#[cfg_attr(kani_smallsort_sorting,cfg(not(kani_smallsort_s2_assumed)))]\n'+PFC]
        for replacement in cases:
            (self.root/BATCH).write_text(self.sources[BATCH]); self.replace(BATCH,PFC,replacement)
            with self.subTest(replacement=replacement),self.assertRaisesRegex(c.GateError,'sort8_stable.*no active matching'):self.check()

    def test_active_nested_cfg_attr_registration(self):
        self.replace(BATCH,PFC,'#[cfg_attr(all(kani,any(kani_smallsort_s2_assumed,not(kani_smallsort_sorting))),kani::proof_for_contract(sort8_stable))]')
        self.assertEqual(self.check()['status'],'STATIC_PASS')

    def test_foreign_same_basename_pfc_cannot_match(self):
        p=self.root/HELPER;p.write_text(p.read_text()+'\n#[kani::ensures(|_|true)]\npub(super) fn sort8_stable() {}\n')
        self.replace(BATCH,PFC,'use super::helper_contracts::sort8_stable as foreign_sort8;\n#[kani::proof_for_contract(foreign_sort8)]')
        with self.assertRaisesRegex(c.GateError,'sort8_stable.*no active matching'):self.check()

    def test_full_target_and_attribute_aliases(self):
        self.replace(BATCH,PFC,'use super::super::sort8_stable as leaf8;\nuse crate::kani as k;\n#[k::proof_for_contract(leaf8)]')
        self.replace(BATCH,'#[kani::stub_verified(sort8_stable)]','#[crate::kani::stub_verified(crate::slice::sort::shared::smallsort::sort8_stable)]')
        self.replace(BATCH,'#[kani::stub(s2_swap_seam,weak_swap)]', 'use self::s2_swap_seam as seam;\nuse crate::kani::stub as ordinary;\n#[ordinary(seam,weak_swap)]')
        self.assertEqual(self.check()['status'],'STATIC_PASS')

    def test_all_verified_targets_require_registration_even_unselected(self):
        for target in ('sort8_stable','insert_tail','bidirectional_merge','swap_if_less'):
            for rel in (HELPER,BATCH):
                (self.root/rel).write_text(self.sources[rel].replace('#[kani::proof_for_contract('+target+')]','#[kani::proof]'))
            with self.subTest(target=target),self.assertRaisesRegex(c.GateError,target+'.*no active matching'):self.check()

    def test_ordinary_active_inactive_contract_cfg_and_safety_spelling(self):
        declarations=['#[kani::requires(true)]', '#[safety::requires(true)]', '#[kani::modifies(v)]', '#[kani::ensures(|_|true)]',
                      '#[cfg_attr(kani,kani::ensures(|_|true))]', '#[kani::checked_with="check"]', '#[kani::fn_marker="contract"]',
                      '#[cfg_attr(all(kani,kani_smallsort_s2_assumed),safety::requires(true))]']
        for attr in declarations:
            (self.root/BATCH).write_text(self.sources[BATCH]);self.replace(BATCH,'unsafe fn s2_swap_seam',attr+'\nunsafe fn s2_swap_seam')
            with self.subTest(attr=attr),self.assertRaisesRegex(c.GateError,'s2_swap_seam.*active contract attrs'):self.check()
        (self.root/BATCH).write_text(self.sources[BATCH]);self.replace(BATCH,'unsafe fn s2_swap_seam','#[cfg_attr(not(kani),safety::requires(true))]\nunsafe fn s2_swap_seam')
        self.assertEqual(self.check()['status'],'STATIC_PASS')

    def test_body_local_attribute_alias_and_stub_set_fail_closed(self):
        for body in ('use crate::kani::stub as ordinary; #[ordinary(s2_swap_seam,weak_swap)] fn local() {}', 'kani::stub_set!{}'):
            (self.root/BATCH).write_text(self.sources[BATCH])
            self.replace(BATCH, 'fn ordered(v: &[u8]) -> bool {', 'fn ordered(v: &[u8]) -> bool {'+body)
            with self.subTest(body=body),self.assertRaisesRegex(c.GateError,'body-local'):self.check()

    def test_unsupported_target_attribute_fails_closed(self):
        self.replace(BATCH,'unsafe fn s2_swap_seam','#[unknown_contract_macro]\nunsafe fn s2_swap_seam')
        with self.assertRaisesRegex(c.GateError,'unsupported target attribute'):self.check()

    def test_contract_alias_is_detected(self):
        self.replace(BATCH,'unsafe fn s2_swap_seam','use crate::kani::requires as premise;\n#[premise(true)]\nunsafe fn s2_swap_seam')
        with self.assertRaisesRegex(c.GateError,'active contract attrs'):self.check()

    def test_foreign_same_basename_does_not_poison_correct_target(self):
        p=self.root/HELPER;p.write_text(p.read_text()+'\n#[kani::ensures(|_|true)]\npub(super) fn s2_swap_seam() {}\n')
        self.assertEqual(self.check()['status'],'STATIC_PASS')
        self.replace(BATCH,'stub(s2_swap_seam,weak_swap)','stub(super::helper_contracts::s2_swap_seam,weak_swap)')
        with self.assertRaisesRegex(c.GateError,'helper_contracts::s2_swap_seam.*active contract attrs'):self.check()

    def test_imported_provider_and_unselected_targets_are_audited(self):
        self.replace(HELPER,'fn comparison_covers(', '#[safety::requires(true)]\nfn comparison_covers(')
        with self.assertRaisesRegex(c.GateError,'comparison_covers.*active contract attrs'):self.check()

    def test_missing_wrong_cfg_foreign_replacement_and_target(self):
        cases=[('unsafe fn weak_swap','unsafe fn missing_swap'),
               ('unsafe fn weak_swap','#[cfg(not(kani_smallsort_s2_assumed))]\nunsafe fn weak_swap'),
               ('stub(s2_swap_seam,weak_swap)','stub(s2_swap_seam,super::helper_contracts::weak_swap)'),
               ('stub(s2_swap_seam,weak_swap)','stub(super::helper_contracts::s2_swap_seam,weak_swap)')]
        for old,new in cases:
            (self.root/BATCH).write_text(self.sources[BATCH]);self.replace(BATCH,old,new)
            with self.subTest(new=new),self.assertRaisesRegex(c.GateError,'(ordinary (replacement|stub target)|unresolved/foreign target)'):self.check()

    def test_glob_unknown_cfg_ambiguous_alias_computed_target_fail_closed(self):
        cases=[(PFC,'use super::super::*;\n'+PFC,'glob'),
               (PFC,'use super::super::sort8_stable;\n'+PFC,'ambiguous'),
               (PFC,'fn sort8_stable() {}\n'+PFC,'ambiguous'),
               (PFC,'#[cfg(unknown_target_cfg)]\n'+PFC,'unknown cfg'),
               ('unsafe fn s2_swap_seam','#[cfg_attr(unknown_target_cfg,kani::requires(true))]\nunsafe fn s2_swap_seam','unknown cfg'),
               ('stub(s2_swap_seam,weak_swap)','stub($target,weak_swap)','unsupported/ambiguous')]
        for old,new,message in cases:
            (self.root/BATCH).write_text(self.sources[BATCH]);self.replace(BATCH,old,new)
            with self.subTest(new=new),self.assertRaisesRegex(c.GateError,message):self.check()

    def test_comments_and_literals_do_not_register_or_contract(self):
        self.replace(BATCH,PFC,'// '+PFC+'\n#[doc="#[kani::proof_for_contract(sort8_stable)]"]')
        with self.assertRaisesRegex(c.GateError,'no active matching'):self.check()
        (self.root/BATCH).write_text(self.sources[BATCH]);self.replace(BATCH,'unsafe fn s2_swap_seam','// #[safety::requires(false)]\n#[doc="#[kani::ensures(false)]"]\nunsafe fn s2_swap_seam')
        self.assertEqual(self.check()['status'],'STATIC_PASS')

    def test_inactive_root_and_module_rejected(self):
        self.replace(BATCH,'fn general32_weak()','#[cfg(not(kani_smallsort_s2_assumed))]\nfn general32_weak()')
        with self.assertRaisesRegex(c.GateError,'manifest root inactive/missing'):self.check()
        (self.root/BATCH).write_text(self.sources[BATCH]);self.request['flags']['RUSTFLAGS']='--cfg=kani_smallsort_sorting --cfg=kani_smallsort_controls'
        with self.assertRaisesRegex(c.GateError,'inactive module'):self.check()

    def test_frozen_hash_and_real_prebuild_call_path(self):
        self.replace(BATCH,'let mut src: [u8;8]','let mut src: [u8; 8]')
        with self.assertRaisesRegex(c.GateError,'source-hash binding drift'):c.check(self.root,runner.load_request())
        import s2_policy
        for gate in (o,c):
            with mock.patch.object(gate,'check',side_effect=c.GateError('gate sentinel')):
                with self.assertRaisesRegex(c.GateError,'gate sentinel'):s2_policy.validate_source(self.root,runner.load_request())
        doc=cp.load_yaml((HERE.parent/'.github/workflows/ch8-s2.yml').read_text());steps=doc['jobs']['s2_batch']['steps']
        a=next(i for i,s in enumerate(steps) if s['name']=='Check all source identities');b=next(i for i,s in enumerate(steps) if s['name']=='Build exact stock tool once')
        steps[a],steps[b]=steps[b],steps[a]
        import yaml
        p=self.root/'wrong-order.yml';p.write_text(yaml.safe_dump(doc))
        with self.assertRaises(AssertionError):cp.check_yaml(p)

    def test_exact_copy_correspondence_and_preserved_relations(self):
        small=self.sources[correspondence.SMALLSORT];batch=self.sources[BATCH]
        self.assertEqual(len(correspondence.check(batch,small)['copies']),3)
        mutations=[('s2_swap_seam(v_base, 0, 12','s2_swap_seam(v_base, 0, 11'),
                   ('let len = v.len();','let len = 1;'),
                   ('S2_NEG_GENERAL32_WEAK','REMOVED_NEGATIVE'),
                   ('stub_verified(sort8_stable)','stub(sort8_stable,diagnostic_sort8)'),
                   ('ptr::copy_nonoverlapping(v.as_ptr(),dst,v.len())','ptr::copy_nonoverlapping(v.as_ptr(),dst,1)')]
        for old,new in mutations:
            self.assertIn(old,batch)
            with self.subTest(old=old),self.assertRaises(c.GateError):correspondence.check(batch.replace(old,new),small)
