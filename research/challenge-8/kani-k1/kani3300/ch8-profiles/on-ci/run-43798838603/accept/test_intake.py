from pathlib import Path
import tempfile
import unittest
import intake


class IntakeTests(unittest.TestCase):
    def test_tool_blocker_preserves_unknown_as_blocked(self):
        r={'unknown_reasons':['unreachable role unresolved'],'pending_reasons':['required post unreachable']}
        self.assertEqual(intake.decision({'expected':'SUCCESS'},{'checks':{'failure':['tool']}},r,[{'id':'tool'}]),'BLOCKED_TOOL')
        self.assertEqual(intake.decision({'expected':'SUCCESS'},{'checks':{'failure':['tool','target']}},r,[{'id':'tool'}]),'REJECTED')

    def test_foreign_positive_failure_rejected(self):
        self.assertEqual(intake.decision({'expected':'SUCCESS'},{'checks':{'failure':['foreign']}},
            {'unknown_reasons':[],'pending_reasons':['POSITIVE_NOT_SUCCESS']},[]),'REJECTED')

    def test_foreign_negative_failure_rejected(self):
        self.assertEqual(intake.decision({'expected':'DETECTED'},{},
            {'unknown_reasons':[],'pending_reasons':['PREDECLARED_NEGATIVE_ORACLE_MISMATCH']},[]),'REJECTED')

    def test_unknown_cannot_be_accepted(self):
        self.assertEqual(intake.decision({'expected':'SUCCESS'},{},
            {'unknown_reasons':['missing input'],'pending_reasons':[]},[]),'PENDING')

    def test_exact_instrumentation_role_and_wrong_site(self):
        fn='kani::mem_init::MemoryInitializationState::get::<8>'
        p=dict(id=fn+'.assertion.1',function=fn,file='library/kani_core/src/mem_init.rs',line=93,
               column=46,description='attempt to add with overflow',status='UNREACHABLE')
        self.assertEqual(intake.instrumentation_role(p)['role'],'instrumentation_defensive_branch')
        for changes in [{'line':118},{'column':45},{'description':'actual initialization predicate'},
                        {'file':'library/core/src/lib.rs'},{'function':'kani::mem_init::unreviewed::<8>'}]:
            self.assertIsNone(intake.instrumentation_role(dict(p,**changes)))

    def test_literal_required_post_never_instrumentation(self):
        p=dict(id='f.assertion.1',function='f',file='x.rs',line=1,column=1,
               description='|_| sorted(v)',status='UNREACHABLE')
        self.assertEqual(intake.required_role(p,{'x.rs':'#[kani::ensures(|_| sorted(v))]'})['role'],'postcondition')
        self.assertIsNone(intake.instrumentation_role(p))

    def test_selected_multiline_record_and_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'stdout.log'
            p.write_text('noise\nCheck 1: f.assertion.1\n - Status: SUCCESS\n - Description: "line one\nline two"\n - Location: x.rs:1:2 in function f\n\nCheck 2: g.assertion.1\n - Status: SUCCESS\n - Description: "other"\n - Location: x.rs:3:4 in function g\n')
            self.assertEqual(intake.select_records(p,{'f.assertion.1'})['f.assertion.1']['description'],'line one\nline two')
            with self.assertRaises(ValueError): intake.select_records(p,{'absent.assertion.1'})

    def test_unsupported_requires_exact_class_site_and_status(self):
        pid='f.unsupported_construct.1'
        u=dict(id=pid,status='SUCCESS',description='unsupported',file='/export/x.rs',line='3',
               **{'class':'unsupported_construct'})
        p=dict(id=pid,status='SUCCESS',description='unsupported',file='x.rs',line=3)
        self.assertEqual(intake.fresh_unsupported_links({'unsupported_constructs':[u]},{pid:p})[pid]['semantics'],
                         'assert(false); assume(false)')
        for changes in [{'status':'FAILURE'},{'line':4},{'description':'other'}]:
            with self.assertRaises(ValueError):
                intake.fresh_unsupported_links({'unsupported_constructs':[u]},{pid:dict(p,**changes)})


if __name__=='__main__': unittest.main()
