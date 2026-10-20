"""Isolated source-map admission controls; no compiler/proof/tool execution."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('a1_tool_overlay', Path(__file__).with_name('a1-tool.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def inputs():
    before = {module.TR: '1'*64, module.SCHEMA: '2'*64, module.EXPORTER: '3'*64}
    after = {**before, module.TR: '4'*64}
    profile = {'r_representation_after': before, 'r_after': after,
               'c_before': dict(after), 'c_after': {**after, module.TR: '5'*64},
               'native_signature_patch_sha256': '6'*64}
    manifest = {'mode': 'SCHEMA_BOUND_IMPL_SIGNATURE_SPECIALIZATION',
                'patch_sha256': '6'*64,
                'files': {module.TR: {'base_sha256': '1'*64, 'result_sha256': '4'*64}}}
    return profile, manifest


class OverlayMapControls(unittest.TestCase):
    def test_exact_dependency_chain(self):
        p,m=inputs()
        self.assertEqual(module.native_signature_overlay_maps(p,m),
                         (p['r_representation_after'], {module.TR:'1'*64}, {module.TR:'4'*64}))

    def test_missing_null_and_wrong_shape_profiles(self):
        for key in ('r_representation_after','r_after','c_before','c_after','native_signature_patch_sha256'):
            for replacement in (None, {}, 'bad'):
                p,m=inputs();p[key]=replacement
                with self.subTest(key=key,replacement=replacement), self.assertRaises(RuntimeError):
                    module.native_signature_overlay_maps(p,m)

    def test_wrong_manifest_or_patch_identity(self):
        for mutate in (lambda m:m.update(mode='OTHER'), lambda m:m.update(files={}),
                       lambda m:m.update(patch_sha256='7'*64),
                       lambda m:m['files'][module.TR].update(base_sha256='8'*64),
                       lambda m:m['files'][module.TR].update(result_sha256='9'*64)):
            p,m=inputs();mutate(m)
            with self.assertRaises(RuntimeError): module.native_signature_overlay_maps(p,m)

    def test_no_unrelated_source_or_C_source_drift(self):
        for section in ('r_after','c_before','c_after'):
            for key in (module.SCHEMA,module.EXPORTER):
                p,m=inputs();p[section][key]='9'*64
                with self.subTest(section=section,key=key), self.assertRaises(RuntimeError):
                    module.native_signature_overlay_maps(p,m)

    def test_malformed_hashes_and_unchanged_overlay(self):
        for value in (None, True, '', 'x'*64, 'A'*64):
            p,m=inputs();p['r_representation_after'][module.TR]=value;m['files'][module.TR]['base_sha256']=value
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                module.native_signature_overlay_maps(p,m)
        p,m=inputs();p['r_representation_after'][module.TR]='4'*64;m['files'][module.TR]['base_sha256']='4'*64
        with self.assertRaises(RuntimeError):module.native_signature_overlay_maps(p,m)


if __name__=='__main__':unittest.main()
