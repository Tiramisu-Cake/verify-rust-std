#!/usr/bin/env python3
"""Synthetic path-policy checks; no proof preparation or Cloud calls."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r23_transport_policy',HERE.parent/'source-input.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class TransportPolicyTests(unittest.TestCase):
    def test_only_four_vps_files_omitted_for_merge(self):
        runtime=['research/challenge-8/cloud-build/'+name for name in ['provider.py','source-input.py','proof-audit.py','package-evidence.py','verify-evidence.py','coordination.py']]
        all_paths=runtime+sorted(m.MERGE_VPS_ONLY_INFRA_PATHS)
        with patch.object(m,'root_tree_of',return_value='0'*40),patch.object(m,'list_committed_tree',side_effect=[all_paths,[]]*3):
            merge=m.infra_paths(Path('/synthetic'),'a'*40,lane='merge')
            stock=m.infra_paths(Path('/synthetic'),'a'*40,lane='stock')
            old=m.infra_paths(Path('/synthetic'),'a'*40)
        self.assertEqual(set(stock)-set(merge),m.MERGE_VPS_ONLY_INFRA_PATHS)
        self.assertEqual(stock,old)
        self.assertTrue(set(runtime).issubset(merge))
        self.assertEqual(len(m.MERGE_VPS_ONLY_INFRA_PATHS),4)

    def test_merge_restore_rejects_vps_and_unknown_paths(self):
        recipe={'lane':'merge','infra_paths':['research/challenge-8/cloud-build/run-merge.sh']}
        base=list(m.INFRA_EXACT_PATHS)+recipe['infra_paths']+[m.RECIPE_PREFIX+'merge.json','research/challenge-8/cloud-build/provider.py']
        record=lambda paths:{'paths':[{'path':p} for p in sorted(paths)]}
        self.assertEqual(m.expected_infra_paths(record(base),recipe),sorted(base))
        for extra in [*m.MERGE_VPS_ONLY_INFRA_PATHS,'unapproved/escape.py']:
            with self.subTest(extra=extra),self.assertRaises(SystemExit):m.expected_infra_paths(record(base+[extra]),recipe)

if __name__=='__main__':unittest.main()
