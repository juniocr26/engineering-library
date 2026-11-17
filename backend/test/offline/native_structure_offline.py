import unittest
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('native_structure',Path(__file__).resolve().parents[2]/'lib/documentation/native_structure.py')
native_structure=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(native_structure)

class CompleteDefinitionTest(unittest.TestCase):
    def test_class_template_methods_include_the_template_declaration(self):
        source='using namespace Base;\n\ntemplate<class scalar>\nscalar Vector3<scalar>::Length() const\n{\n return x*x;\n}\n'
        spans=native_structure.ranges(source)
        self.assertEqual(1,len(spans));span=spans[0]
        self.assertEqual('Vector3::Length',span['qualified']);self.assertEqual('Vector3',span['owner'])
        self.assertTrue(''.join(source.splitlines(keepends=True)[span['start']:span['end']]).startswith('template<class scalar>'))
    def test_free_templates_remain_unsupported(self):
        self.assertEqual([],native_structure.ranges('template<class T>\nT helper(T x) { return x; }\n'))
    def test_specializations_and_nested_templates_remain_unsupported(self):
        for source in ['template<>\nfloat Vector<float>::Length() { return 1; }\n','template<class T, class U>\nT Vector<T>::Length() { return 1; }\n']:
            self.assertEqual([],native_structure.ranges(source))
    def test_csharp_ordinary_method_preserves_struct_owner(self):
        source='namespace Game {\n public readonly struct WDist : IComparable {\n public static WDist FromCells(int cells) { return new WDist(1024 * cells); }\n }\n}\n'
        span=native_structure.ranges(source)[0];self.assertEqual('WDist',span['owner']);self.assertEqual('Game::WDist::FromCells',span['qualified'])
    def test_requires_expression_is_not_mistaken_for_the_function_body(self):
        source='template<class T>\nT Box<T>::get() const requires requires(T t) { t.value(); }\n{\n return value;\n}\n'
        self.assertEqual([],native_structure.ranges(source))
    def test_preprocessor_body_is_still_rejected(self):
        self.assertEqual([],native_structure.ranges('float f() {\n#if FLAG\n return 1;\n#else\n return 2;\n#endif\n}\n'))

if __name__=='__main__':unittest.main()
