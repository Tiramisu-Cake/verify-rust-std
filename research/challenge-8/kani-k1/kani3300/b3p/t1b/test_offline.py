"""Synthetic preservation checks; no artifact or toolchain execution."""
import runpy
import tempfile
import unittest
from pathlib import Path

M = runpy.run_path(str(Path(__file__).with_name('offline.py')))
normalize, check_control = M['normalize'], M['check_control']

def block(name, typ, value='', flags='type auxiliary', pretty='', module='', location='', base=None):
    return (f'Symbol......: {name}\nPretty name.: {pretty}\nModule......: {module}\n'
            f'Base name...: {name if base is None else base}\nMode........: C\nType........: {typ}\n'
            f'Value.......: {value}\nFlags.......: {flags}\nLocation....: {location}\n\n')

def dump(*blocks):
    return '\nSymbols:\n\n' + ''.join(blocks)

def canonical(text):
    return normalize(text)[0]

def allocation(n, data):
    ident = f'c::AllocId({n}, ThreadLocalIndex)'
    return block(ident, 'const struct '+ident+'::struct', data, 'lvalue static_lifetime state_var') + block('tag-'+ident+'::struct', 'struct '+ident+'::struct { unsigned char 0[1]; }')

class OfflineTests(unittest.TestCase):
    def test_alloc_bijection_and_content_order(self):
        def model(a,b,byte=9,ref=None):
            x=f'c$$AllocId({a}, ThreadLocalIndex)';y=f'c$$AllocId({b}, ThreadLocalIndex)'
            init=block('__CPROVER_initialize','void (void)', '{\n  '+x+' = { .0={ 7 } };\n  '+y+f' = {{ .0={{ {byte} }} }};\n'+'}', 'lvalue')
            use=block('f','void (void)','{\n  p = &'+(x if ref is None else y)+';\n  q = &'+y+';\n}', 'lvalue')
            return dump(allocation(a,'{ .0={ 7 } }'),allocation(b,f'{{ .0={{ {byte} }} }}'),init,use)
        a,b=model(2,10),model(20,1)
        self.assertEqual(canonical(a),canonical(b))
        self.assertNotEqual(canonical(a),canonical(model(20,1,byte=8)))
        self.assertNotEqual(canonical(a),canonical(model(20,1,ref='changed')))
        self.assertIn('AllocId(1, ThreadLocalIndex)', canonical(a))

    def test_alloc_literal_is_semantic_data(self):
        def d(n,literal):
            return dump(allocation(n,'{ .0={ 7 } }'), block('f','void (void)',
                '{\n  p = &c$$AllocId('+str(n)+', ThreadLocalIndex);\n  puts("'+literal+'");\n}', 'lvalue'))
        a=d(2,'AllocId(20, ThreadLocalIndex)')
        b=d(99,'AllocId(20, ThreadLocalIndex)')
        self.assertEqual(canonical(a),canonical(b))
        self.assertNotEqual(canonical(a),canonical(d(99,'AllocId(30, ThreadLocalIndex)')))

    def test_symbol_record_order_only(self):
        a=block('a','int');b=block('b','long int')
        self.assertEqual(canonical(dump(a,b)),canonical(dump(b,a)))
        self.assertNotEqual(canonical(dump(a,b)),canonical(dump(a,block('b','int'))))

    def test_initialize_reorder_only_address_constant_assignments(self):
        a='c$$AllocId(1, ThreadLocalIndex)';b='c$$AllocId(2, ThreadLocalIndex)'
        aa='  '+a+' = { .0={ 7 } };\n';bb='  '+b+' = { .0={ 9 } };\n'
        records=allocation(1,'{ .0={ 7 } }')+allocation(2,'{ .0={ 9 } }')
        def d(body):return dump(records,block('__CPROVER_initialize','void (void)','{\n'+body+'}', 'lvalue'))
        self.assertEqual(canonical(d(aa+bb)),canonical(d(bb+aa)))
        self.assertNotEqual(canonical(d(aa+'  observed = '+a+';\n'+bb)),canonical(d(bb+'  observed = '+a+';\n'+aa)))
        self.assertNotEqual(canonical(d(aa+'  call();\n'+bb)),canonical(d(bb+'  call();\n'+aa)))
        with self.assertRaisesRegex(ValueError,'duplicate'):
            canonical(d(aa+aa))

    def test_init_dereference_is_never_reordered(self):
        n='c::AllocId(1, ThreadLocalIndex)'
        rhs='*(&c$$AllocId(2, ThreadLocalIndex))'
        stat=block(n,'const int',rhs,'lvalue static_lifetime state_var')
        init=block('__CPROVER_initialize','void (void)',
            '{\n  c$$AllocId(1, ThreadLocalIndex) = '+rhs+';\n}', 'lvalue')
        blocks=M['parse'](dump(stat,init))[1]
        self.assertEqual(init,M['initialize_order'](init,blocks,{}))

    def test_multiline_pure_pointer_aggregate_commutes(self):
        a='c::AllocId(1, ThreadLocalIndex)';b='c::AllocId(2, ThreadLocalIndex)'
        pa=a.replace('::','$$');pb=b.replace('::','$$')
        rhs='{ .0=byte_extract_little_endian((signed char *)((unsigned char *)&'+pb+' + 0), 0, signed char *), .1={ 4, 0 },\n    .2=byte_extract_little_endian((signed char *)((unsigned char *)&'+pb+' + 0), 0, signed char *), .3={  } }'
        defs=block(a,'const struct A',rhs,'lvalue static_lifetime state_var')+allocation(2,'{ .0={ 7 } }')
        one='  '+pa+' = '+rhs+';\n';two='  '+pb+' = { .0={ 7 } };\n'
        def d(body):return dump(defs,block('__CPROVER_initialize','void (void)','{\n'+body+'}', 'lvalue'))
        self.assertEqual(canonical(d(one+two)),canonical(d(two+one)))
        # A scalar read through the pointer does not qualify as a pure address.
        bad=rhs.replace('byte_extract_little_endian((signed char *)((unsigned char *)&'+pb+' + 0), 0, signed char *)','*(&'+pb+')')
        entry=block(a,'const struct A',bad,'lvalue static_lifetime state_var')
        init=block('__CPROVER_initialize','void (void)','{\n  '+pa+' = '+bad+';\n}', 'lvalue')
        self.assertEqual(init,M['initialize_order'](init,M['parse'](dump(entry,init))[1],{}))

    def test_vtable_comment_ids_only(self):
        comment='/* Kani-internal sanity check: Correct CBMC vtable size for StructTag("tag-_77") (MIR type Ty { id: 20, kind: RigidTy(Adt(AdtDef(DefId { id: 30, name: "T" }))) }). Please report failures:\nhttps://github.com/model-checking/kani/issues/new?template=bug_report.md */'
        def d(c, assertion='assert(sizeof(int) == 4);'):return dump(block('f','void (void)','{\n'+c+'\n'+assertion+'\n}', 'lvalue'))
        a=d(comment)
        self.assertEqual(canonical(a),canonical(d(comment.replace('id: 20','id: 99').replace('id: 30','id: 40'))))
        self.assertNotEqual(canonical(a),canonical(d(comment.replace('tag-_77','tag-_78'))))
        self.assertNotEqual(canonical(a),canonical(d(comment.replace('"T"','"U"'))))
        self.assertNotEqual(canonical(a),canonical(d(comment,'assert(sizeof(int) == 8);')))

    def test_builtin_location_narrow(self):
        def d(loc,typ='__CPROVER_bool',name='__CPROVER_malloc_is_new_array',module='<built-in-library>'):
            return dump(block(name,typ,flags='lvalue static_lifetime',module=module,location=loc))
        a=d('file <builtin-library-malloc> line 6')
        self.assertEqual(canonical(a),canonical(d('file <builtin-library-calloc> line 8')))
        self.assertEqual(canonical(a),canonical(d('file <builtin-library-free> line 11')))
        self.assertNotEqual(canonical(a),canonical(d('file <builtin-library-calloc> line 9')))
        self.assertNotEqual(canonical(a),canonical(d('file <builtin-library-calloc> line 8',typ='int')))
        self.assertNotEqual(canonical(d('file a',name='x')),canonical(d('file b',name='x')))

    def local_model(self, alternate=False, semantic_change=False):
        owner='_Rowner'
        n1=owner+'::1::var_10::input';n2=owner+'::1::var_12::input'
        q1=n1.replace('::','$$');q2=n2.replace('::','$$')
        x,y=('input',q2) if alternate else (q1,'input')
        rhs=y if semantic_change else x
        value='{\n  short int '+x+';\n  struct S '+y+';\n\nbb0:\n  '+x+' = 7;\n  '+y+' = { .input='+rhs+' };\n  p->input = 9;\n  puts("input"); /* input */\n}'
        return dump(block(owner,'void (void)',value,'lvalue'),block(n1,'short int',flags='lvalue thread_local auxiliary',base='input'),block(n2,'struct S',flags='lvalue thread_local auxiliary',base='input'))

    def test_local_alpha_binding_preserves_members_and_strings(self):
        a,b=self.local_model(),self.local_model(True)
        self.assertEqual(canonical(a),canonical(b))
        self.assertIn('p->input = 9;',canonical(a))
        self.assertIn('.input=',canonical(a))
        self.assertIn('puts("input"); /* input */',canonical(a))
        self.assertNotEqual(canonical(a),canonical(self.local_model(True,True)))
        self.assertNotEqual(canonical(a),canonical(b.replace('short int input;','long int input;')))

    def test_local_separate_namespaces_fail_closed(self):
        for collision in ('struct input *p;', 'input: ;', 'goto input;'):
            a=self.local_model().replace('  p->input = 9;', '  '+collision)
            normalized,stats=normalize(a)
            self.assertNotIn('local_names',stats)
        a=self.local_model(True)
        b=a.replace('p->input = 9;', 'p->input = 10;')
        self.assertNotEqual(canonical(a),canonical(b))

    def control_model(self,new=False):
        parent='_123';wrap=parent+'::zst_array'
        return dump(block('tag-Unit','struct Unit { }'),
          block('tag-'+parent,'union '+parent+' { unsigned char bytes[8]; struct '+wrap+' zst_array; }',pretty='ArrayUnion'),
          block('tag-'+wrap,'struct '+wrap+' { struct Unit zst_array'+('' if new else '[2]')+'; unsigned long int zst_array_padding; }'))

    def test_control_actual_union_edge_and_shape(self):
        a,b=canonical(self.control_model()),canonical(self.control_model(True))
        self.assertNotEqual(a,b)
        self.assertTrue(check_control(a,b)['valid'])
        self.assertFalse(check_control(a,b.replace('bytes[8]','bytes[9]'))['valid'])
        self.assertFalse(check_control(a,b.replace('struct _123::zst_array zst_array;', 'struct _other::zst_array zst_array;'))['valid'])
        self.assertFalse(check_control(a.replace('[2]','[3]'),b)['valid'])
        self.assertFalse(check_control(a,b.replace('unsigned long int zst_array_padding','unsigned int zst_array_padding'))['valid'])
        self.assertFalse(check_control(a,b.replace('struct Unit { }','struct Unit { char x; }'))['valid'])

    def test_cumulative_pipeline_matches_public_normalizer(self):
        for text in [self.control_model(),self.control_model(True),self.local_model(),self.local_model(True),dump(allocation(9,'{ .0={ 7 } }'))]:
            self.assertEqual(canonical(text),M['stages'](text)[0])

    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'data';root.mkdir()
            with self.assertRaises(ValueError):M['safe_read'](root,'/etc/passwd')
            (Path(tmp)/'other').write_text('data')
            with self.assertRaises(ValueError):M['safe_read'](root,'../other')

if __name__=='__main__':unittest.main()
