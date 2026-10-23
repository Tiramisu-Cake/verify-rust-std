#!/usr/bin/env python3
"""Static profile/registration tests; no actual proof preparation or tool execution."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    __import__('sys').modules[name]=module
    spec.loader.exec_module(module)
    return module

registry=load('r23_profile_service_registry',HERE/'r23-source-profile.py')
profile=json.loads((HERE/'GLUE-PROFILE.json').read_bytes())

class ProfileTests(unittest.TestCase):
    def test_exact_reversal(self):
        baseline=subprocess.check_output(['git','show','733b6a7d68259787f1caf58177060589b6af779e:research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json'],cwd=HERE)
        self.assertEqual(registry.serialize(registry.reverse_profile(profile)),baseline)

    def test_all_fields_and_unknown_fields_fail_closed(self):
        for key in profile:
            candidate=copy.deepcopy(profile);candidate[key]=None
            with self.subTest(key=key),self.assertRaises(ValueError):registry.reverse_profile(candidate)
        candidate=copy.deepcopy(profile);candidate['unregistered_field']=True
        with self.assertRaises(ValueError):registry.reverse_profile(candidate)
        for bad in (None,True,[],{}):
            with self.assertRaises(ValueError):registry.reverse_profile(bad)

    def test_prove_registration_and_source_pins(self):
        prove=load('r23_profile_service_prove',HERE.parents[1]/'merge/overnight/guard-ownership/insertion-onecell/prove.py')
        baseline=(HERE/'R17-BASELINE-PROFILE-20261021.json').read_bytes()
        self.assertTrue(prove.admit_r17_profile_extension_if_present(profile,baseline))
        for key in registry.CANDIDATE_VALUES:
            if key.endswith('_sha256'):
                self.assertTrue(prove._r11_r22_source_pin_matches(profile,{},True,key))
        wrong=copy.deepcopy(profile);wrong['translator_sha256']='0'*64
        with self.assertRaises(ValueError):prove.admit_r17_profile_extension_if_present(wrong,baseline)

    def test_callback_and_provider_admit_exact_profile(self):
        callback=load('r23_profile_service_callback',HERE/'first-callback.py')
        provider=load('r23_profile_service_provider',HERE.parents[1]/'merge/cloud-build/provider-overlays.py')
        self.assertTrue(callback._r22_owned_nll_registration_matches(HERE/'GLUE-PROFILE.json',callback.R11_PROFILE))
        self.assertEqual(provider.profile_identity(profile),provider.R22_OWNED_NLL_PROFILE)
        bad=copy.deepcopy(profile);bad['r23_source_borrow_registration']['source_pins']={}
        with self.assertRaises(ValueError):provider.profile_identity(bad)

    def test_helper_pins_are_bound(self):
        registry.validate_helper_sources(HERE)
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in registry.HELPER_PINS:(root/name).write_bytes((HERE/name).read_bytes())
            registry.validate_helper_sources(root)
            name=next(iter(registry.HELPER_PINS));(root/name).write_bytes(b'corrupted')
            with self.assertRaises(ValueError):registry.validate_helper_sources(root)

if __name__=='__main__':unittest.main()
