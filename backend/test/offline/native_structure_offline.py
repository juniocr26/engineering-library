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

    def test_unicode_literal_prefix_cannot_hide_preprocessor_body(self):
        for separator in ['\u2028', '\u2029', '\x85', '\v', '\f']:
            source = ('const char *marker = "' + ('x' + separator) * 12 + '";\n'
                      'int F() {\n#if FLAG\n return 1;\n#else\n return 2;\n#endif\n}\n')
            with self.subTest(separator=hex(ord(separator))):
                self.assertEqual([], native_structure.ranges(source))

    def test_crlf_ranges_remain_physical_and_bare_cr_is_explicitly_refused(self):
        source = 'int F() {\r\n return 1;\r\n}\r\n'
        self.assertEqual((0, 3), tuple(native_structure.ranges(source)[0][k] for k in ['start', 'end']))
        with self.assertRaisesRegex(ValueError, 'bare CR'):
            native_structure.ranges(source.replace('\r\n', '\r'))

    def test_go_callback_return_keeps_the_whole_outer_definition(self):
        factory = ('func Timeout(timeout time.Duration) func(next http.Handler) http.Handler {\n'
                   ' return func(next http.Handler) http.Handler {\n'
                   '  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {\n'
                   '   next.ServeHTTP(w, r)\n'
                   '  })\n'
                   ' }\n'
                   '}\n')
        source = 'package middleware\n\n' + factory + 'func Next() {}\n'
        spans = native_structure.ranges(source, go=True)
        self.assertEqual(['Timeout', 'Next'], [span['symbol'] for span in spans])
        span = spans[0]
        self.assertEqual('middleware.Timeout', span['qualified'])
        self.assertEqual(factory, ''.join(source.splitlines(keepends=True)[span['start']:span['end']]))

    def test_go_returned_callback_can_have_no_result(self):
        source = 'package discovery\nfunc Name(name string) func(*Manager) {\n return func(m *Manager) { m.name = name }\n}\n'
        spans = native_structure.ranges(source, go=True)
        self.assertEqual(1, len(spans))
        self.assertEqual('discovery.Name', spans[0]['qualified'])

    def test_go_bodyless_declaration_does_not_capture_the_next_function(self):
        source = 'package sample\nfunc Declared()\nfunc Actual() func() { return func() {} }\n'
        spans = native_structure.ranges(source, go=True)
        self.assertEqual(['Actual'], [span['symbol'] for span in spans])
        self.assertEqual(2, spans[0]['start'])

    def test_go_bodyless_declaration_does_not_capture_a_receiver_method(self):
        source = 'package sample\nfunc Declared()\nfunc (receiver Receiver) Actual() bool { return true }\n'
        self.assertEqual([], native_structure.ranges(source, go=True))

    def test_go_nonempty_anonymous_callback_types_stay_unsupported(self):
        for source in [
            'package sample\nfunc F() func() struct{ X int } { return nil }\n',
            'package sample\nfunc F() func(value interface{ Run() }) bool { return nil }\n',
        ]:
            self.assertEqual([], native_structure.ranges(source, go=True))

    def test_go_callback_raw_string_braces_do_not_end_the_outer_span(self):
        factory = 'func Factory() func(string) bool {\n return func(value string) bool {\n  return value == `}`\n }\n}\n'
        source = 'package sample\n' + factory + 'func Other() bool { return true }\n'
        spans = native_structure.ranges(source, go=True)
        self.assertEqual(['Factory', 'Other'], [span['symbol'] for span in spans])
        self.assertEqual(factory, ''.join(source.splitlines(keepends=True)[spans[0]['start']:spans[0]['end']]))

    def test_go_generic_function_remains_unsupported(self):
        source = 'package sample\nfunc Wrap[T any](value T) func() T { return func() T { return value } }\n'
        self.assertEqual([], native_structure.ranges(source, go=True))

    def test_go_callback_tuple_result_remains_unsupported(self):
        source = 'package sample\nfunc Factory() func() (int, error) { return nil }\n'
        self.assertEqual([], native_structure.ranges(source, go=True))

    def test_go_callback_named_pointer_and_slice_results(self):
        for result in ['*Result', '[]Result', '[]*sample.Result']:
            source = 'package sample\nfunc Factory() func() ' + result + ' { return nil }\n'
            spans = native_structure.ranges(source, go=True)
            self.assertEqual(['Factory'], [span['symbol'] for span in spans])

    def test_go_bodyless_callback_result_does_not_consume_later_body(self):
        for result in ['func()', 'func() bool', 'func() http.Handler', 'func() func() bool']:
            source = 'package sample\nfunc External() ' + result + '\nfunc Actual() {}\n'
            spans = native_structure.ranges(source, go=True)
            self.assertEqual(['Actual'], [span['symbol'] for span in spans])
            self.assertEqual(2, spans[0]['start'])


    def test_go_empty_interface_results_keep_outer_body_spans(self):
        for result in ['interface{}', '[]interface{}', 'map[string]interface{}', '([]interface{}, error)']:
            with self.subTest(result=result):
                returned = 'nil, nil' if result.startswith('(') else 'nil'
                factory = 'func Values() ' + result + ' {\n return ' + returned + '\n}\n'
                source = 'package sample\n' + factory + 'func Next() {}\n'
                spans = native_structure.ranges(source, go=True)
                self.assertEqual(['Values', 'Next'], [span['symbol'] for span in spans])
                self.assertEqual(factory, ''.join(source.splitlines(keepends=True)[spans[0]['start']:spans[0]['end']]))

    def test_go_empty_interface_comments_do_not_become_a_type_body(self):
        source = 'package sample\nfunc Value() interface /* type */ { /* empty */ } {\n return nil\n}\n'
        spans = native_structure.ranges(source, go=True)
        self.assertEqual(['Value'], [span['symbol'] for span in spans])
        self.assertEqual([1, 4], [spans[0]['start'], spans[0]['end']])

    def test_go_returned_callback_accepts_empty_interface_parameter_or_result(self):
        for result in ['func(value interface{}) bool', 'func() interface{}']:
            source = 'package sample\nfunc Factory() ' + result + ' {\n return nil\n}\n'
            spans = native_structure.ranges(source, go=True)
            self.assertEqual(['Factory'], [span['symbol'] for span in spans])
            self.assertEqual([1, 4], [spans[0]['start'], spans[0]['end']])

    def test_go_nonempty_interface_and_anonymous_struct_result_still_refused(self):
        for result in ['interface{ Run() }', 'struct{}', 'func() interface{ Run() }', 'interface{ /* marker */ Run() }']:
            source = 'package sample\nfunc Value() ' + result + ' { return nil }\n'
            self.assertEqual([], native_structure.ranges(source, go=True))

    def test_go_bodyless_empty_interface_does_not_absorb_next_definition(self):
        for result in ['interface{}', 'map[string]interface{}', 'func() interface{}']:
            source = 'package sample\nfunc External() ' + result + '\nfunc Actual() {\n}\n'
            spans = native_structure.ranges(source, go=True)
            self.assertEqual(['Actual'], [span['symbol'] for span in spans])
            self.assertEqual([2, 4], [spans[0]['start'], spans[0]['end']])

    def test_go_bodyless_empty_interface_does_not_absorb_receiver_body(self):
        source = 'package sample\nfunc External() []interface{}\nfunc (r Receiver) Actual() {}\n'
        self.assertEqual([], native_structure.ranges(source, go=True))

    def test_go_empty_interface_text_in_raw_string_preserves_outer_end(self):
        source = 'package sample\nfunc Value() interface{} {\n return `interface{} }`\n}\n'
        spans = native_structure.ranges(source, go=True)
        self.assertEqual(['Value'], [span['symbol'] for span in spans])
        self.assertEqual([1, 4], [spans[0]['start'], spans[0]['end']])

    def test_go_adjacent_same_line_definition_remains_refused(self):
        source = 'package sample\nfunc Value() interface{} { return nil }; func Hidden() {}\nfunc Actual() {}\n'
        self.assertEqual(['Actual'], [span['symbol'] for span in native_structure.ranges(source, go=True)])

if __name__=='__main__':unittest.main()
