#!/usr/bin/env python3
"""Synthetic tool checks only. No Rust/compiler invocation."""
import unittest
from check_seams import inventory, generic_impl_errors, import_leaves, call_arity

class Seams(unittest.TestCase):
    def errors(self,text):
        rows,ts,_=inventory(text)
        return generic_impl_errors(rows,ts,'synthetic.rs')

    def test_missing_trait_impl_lifetime(self):
        self.assertEqual(len(self.errors("struct Visitor<'a> { x: &'a u8 } impl Trait for Visitor {}")),1)

    def test_explicit_trait_impl_lifetime(self):
        self.assertEqual(self.errors("struct Visitor<'a> { x: &'a u8 } impl Trait for Visitor<'_> {}"),[])

    def test_inherent_impl_generic_missing(self):
        self.assertEqual(len(self.errors('struct Registry<T> { x: T } impl Registry {}')),1)

    def test_explicit_inherent_impl(self):
        self.assertEqual(self.errors('struct Registry<T> { x: T } impl<T> Registry<T> {}'),[])

    def test_cross_file_impl(self):
        rows,ts,_=inventory('impl Trait for Visitor {}')
        self.assertEqual(len(generic_impl_errors(rows,ts,'consumer.rs',{'Visitor':1})),1)

    def test_wrong_generic_argument_count(self):
        self.assertEqual(len(self.errors("struct Visitor<'a,T> { x: &'a T } impl<T> Trait for Visitor<T> {}")),1)

    def test_comments_and_literals_do_not_create_declarations(self):
        rows,_,_=inventory('/* struct Fake<T> {} */ fn real() { let s = r#"impl Fake {}"#; let c = \'x\'; }')
        self.assertEqual([(r['kind'],r['name']) for r in rows],[('fn','real')])

    def test_nested_imports_and_aliases(self):
        self.assertEqual(import_leaves('use crate :: { a :: A , b :: { B , C as D } }'),
                         {('crate','a','A'),('crate','b','B'),('crate','b','C','as','D')})

    def test_arity_nested_and_turbofish(self):
        _,ts,pairs=inventory('fn x() { f(a, g::<A, B>(b, c), [1,2],); }')
        i=next(i for i,t in enumerate(ts) if t[0]=='f')+1
        self.assertEqual(call_arity(ts,i,pairs),3)

    def test_missing_argument_detectable(self):
        _,ts,pairs=inventory('fn x() { Visitor::new(body); }')
        i=next(i for i,t in enumerate(ts) if t[0]=='new')+1
        self.assertNotEqual(call_arity(ts,i,pairs),2)

if __name__=='__main__': unittest.main()
