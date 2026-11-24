"""Real packaged-parser controls plus fail-closed launcher integrity checks."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('go_source_ast', ROOT / 'tools/go_source_ast.py')
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


class GoSourceAstTests(unittest.TestCase):
    def packet(self, source, selectors=('F',)):
        return TOOL.run(json.dumps(dict(source=source, path='sample.go', selectors=selectors)).encode())

    def test_ordered_guard_chain_preserves_conditions_and_return_expressions(self):
        source = '''package p
func F(value, fallback int) int {
 if value == 0 { return fallback }
 if value < 1 { return 1 }
 if value > 100 { return 100 }
 return value
}
'''
        unit = self.packet(source)['units'][0]
        chain = unit['if_return_chain_contract']
        self.assertEqual(['if-return', 'if-return', 'if-return', 'return'], chain['source_statement_order'])
        self.assertEqual(['value == 0', 'value < 1', 'value > 100'], [g['condition'] for g in chain['guards']])
        self.assertEqual([['fallback'], ['1'], ['100']], [g['true_return_contract']['expressions'] for g in chain['guards']])
        self.assertEqual(['value'], chain['fallthrough_return_contract']['expressions'])
        self.assertEqual([3, 4, 5], [g['line'] for g in chain['guards']])
        self.assertFalse(chain['types_resolved'])
        self.assertFalse(chain['runtime_completion_verified'])
        self.assertNotIn('if_return_contract', unit)

    def test_guard_chain_declines_initializer_else_nested_work_and_excess_guards(self):
        for body in [
            'if x := value; x == 0 { return 0 }; if b { return 1 }; return 2',
            'if a { return 0 }; if b { return 1 } else { return 2 }; return 3',
            'if a { if b { return 0 } }; if c { return 1 }; return 2',
            'if a { prepare(); return 0 }; if b { return 1 }; return 2',
            'if a { return 0 }; prepare(); if b { return 1 }; return 2',
            'if a { return 0 }; if b { return 1 }; if c { return 2 }; if d { return 3 }; return 4',
            'if a { return }; if b { return 1 }; return 2',
            'if a { return 0 }; if b { return 1 }; prepare()',
        ]:
            with self.subTest(body=body):
                unit = self.packet('package p\nfunc F() int {\n' + body + '\n}\n')['units'][0]
                self.assertNotIn('if_return_chain_contract', unit)

    def test_guard_chain_lines_ignore_logical_line_directives(self):
        source = 'package p\n//line logical.go:700\nfunc F(value int) int {\n if value == 0 { return 7 }\n if value < 1 { return 1 }\n return value\n}\n'
        for text in [source, source.replace('\n', '\r\n')]:
            unit = self.packet(text)['units'][0]
            self.assertEqual([3, 7], [unit['start_line'], unit['end_line']])
            self.assertEqual([4, 5], [g['line'] for g in unit['if_return_chain_contract']['guards']])

    def test_handler_defer_order_is_scoped_to_the_exact_callback(self):
        source = '''package p
func F(next http.Handler) http.Handler {
 fn := func(w http.ResponseWriter, r *http.Request) {
  defer func() { _ = recover() }()
  next.ServeHTTP(w, r)
 }
 return http.HandlerFunc(fn)
}
'''
        contract = self.packet(source)['units'][0]['handler_defer_contract']
        self.assertEqual(['defer-registration', 'direct-call'], contract['source_statement_order'])
        self.assertEqual('next.ServeHTTP(w, r)', contract['direct_call_expression'])
        self.assertLess(contract['deferred_body_end_line'], contract['direct_call_line'])
        self.assertFalse(contract['deferred_body_analyzed'])
        self.assertFalse(contract['types_resolved'])
        self.assertFalse(contract['runtime_completion_verified'])

    def test_handler_defer_order_does_not_confuse_an_immediate_inner_scope(self):
        source = '''package p
func F(next http.Handler) http.Handler {
 fn := func(w http.ResponseWriter, r *http.Request) {
  func() { defer func() { _ = recover() }(); panic("synthetic") }()
  next.ServeHTTP(w, r)
 }
 return http.HandlerFunc(fn)
}
'''
        self.assertNotIn('handler_defer_contract', self.packet(source)['units'][0])

    def test_handler_defer_order_declines_argument_effects_and_extra_statements(self):
        template = '''package p
func F(next http.Handler) http.Handler {
 fn := func(w http.ResponseWriter, r *http.Request) {
  %s
 }
 return http.HandlerFunc(fn)
}
'''
        for body in [
            'defer func(v any) { _ = recover() }(prepare()); next.ServeHTTP(w, r)',
            'defer func() { _ = recover() }(); next.ServeHTTP(writer(), r)',
            'defer func() { _ = recover() }(); prepare(); next.ServeHTTP(w, r)',
            'defer func() { next.ServeHTTP(w, r) }(); return',
        ]:
            with self.subTest(body=body):
                self.assertNotIn('handler_defer_contract', self.packet(template % body)['units'][0])

    def test_if_return_preserves_guard_tuple_order_and_unresolved_helper(self):
        source = 'package p\nfunc F() (any,error) { if err != nil { return nil,err }; return helper() }\nfunc init(){ panic("must never execute") }\n'
        unit = self.packet(source)['units'][0]
        contract = unit['if_return_contract']
        self.assertEqual('err != nil', contract['condition'])
        self.assertEqual(['nil', 'err'], contract['true_return_contract']['expressions'])
        self.assertEqual(['helper()'], contract['fallthrough_return_contract']['expressions'])
        self.assertFalse(contract['runtime_completion_verified'])
        self.assertNotIn('return_contract', unit)
        self.assertNotIn('deferred_return_contract', unit)

    def test_if_return_refuses_initializer_else_extra_and_nonexplicit_returns(self):
        for body in [
            'if x := f(); x { return 1 }; return 0',
            'if x { return 1 } else { return 0 }; return 2',
            'prepare(); if x { return 1 }; return 0',
            'if x { prepare(); return 1 }; return 0',
            'if x { return }; return 0',
            'if x { return 1 }; return',
            'if x { return func() int { return 1 } }; return f',
            'if x { return State{} }; return zero'
        ]:
            with self.subTest(body=body):
                self.assertNotIn('if_return_contract', self.packet('package p\nfunc F() int {' + body + '}')['units'][0])


    def test_real_parser_preserves_unicode_crlf_source_and_physical_line_directive(self):
        source = 'package p\r\n//line fiction.go:999\r\nfunc F() string { return "ação" }\r\n'
        result = self.packet(source)
        unit = result['units'][0]
        self.assertEqual(3, unit['start_line'])
        self.assertEqual(3, unit['end_line'])
        self.assertEqual(source.split('\n')[2], unit['quote'])
        self.assertTrue(result['syntax_only'])
        self.assertFalse(result['source_executed'])
        self.assertEqual(64, len(result['producer']['binary_sha256']))

    def test_receiver_qualification_resolves_bare_name_ambiguity(self):
        source = 'package p\nfunc (x A) F() {}\nfunc (x *B[T]) F() {}\n'
        with self.assertRaisesRegex(ValueError, '2 matches'):
            self.packet(source)
        unit = self.packet(source, ['p.B.F'])['units'][0]
        self.assertEqual('p.B.F', unit['symbol'])
        self.assertEqual(3, unit['start_line'])

    def test_generic_function_and_anonymous_result_use_actual_ast(self):
        source = 'package p\nfunc F[T any](x T) struct{ Value T } { return struct{ Value T }{x} }\n'
        self.assertEqual('p.F', self.packet(source)['units'][0]['symbol'])

    def test_factory_signature_distinguishes_returned_callback(self):
        source = 'package p\nfunc F(n int) func(string) (int,error) { return func(s string) (int,error) { return n,nil } }\n'
        factory = self.packet(source)['units'][0]['factory']
        self.assertEqual('func(n int) func(string) (int, error)', factory['outer_function_type'])
        self.assertEqual('func(s string) (int, error)', factory['returned_literal_type'])
        self.assertEqual(1, factory['callback_body_statements'])

    def test_work_before_callback_return_does_not_claim_sole_return_profile(self):
        source = 'package p\nfunc F() func() { n := 1; return func() { _ = n } }\n'
        self.assertNotIn('factory', self.packet(source)['units'][0])

    def test_deferred_return_is_separate_from_sole_return_and_runtime_mutex_proof(self):
        source = 'package p\nfunc F() bool { mu.RLock(); defer mu.RUnlock(); return cancel != nil }\n'
        unit = self.packet(source)['units'][0]
        self.assertNotIn('return_contract', unit)
        contract = unit['deferred_return_contract']
        self.assertEqual(['call', 'defer', 'return'], contract['source_statement_order'])
        self.assertEqual('mu.RLock()', contract['call'])
        self.assertEqual('mu.RUnlock()', contract['deferred_call'])
        self.assertEqual(['cancel != nil'], contract['return_contract']['expressions'])
        self.assertFalse(contract['type_or_mutex_behavior_verified'])
        self.assertFalse(contract['runtime_completion_verified'])
        self.assertNotIn('deferred_return_contract', self.packet(source.replace('defer ', ''))['units'][0])

    def test_source_text_is_not_executed_or_import_resolved(self):
        # Missing import and init body are deliberately never resolved/run.
        source = 'package p\nimport "missing.invalid/private"\nfunc init() { panic("must not execute") }\nfunc F() { panic("must not execute") }\n'
        self.assertEqual('p.F', self.packet(source)['units'][0]['symbol'])

    def test_syntax_diagnostic_anywhere_refuses_partial_ast(self):
        with self.assertRaisesRegex(ValueError, 'syntax refused'):
            self.packet('package p\nfunc F() {}\nfunc Broken( {\n')

    def test_bodyless_and_adjacent_same_line_code_refused(self):
        for source in ['package p\nfunc F()\n', 'package p\nfunc F() {}; func G() {}\n']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                self.packet(source)

    def test_aliases_cannot_select_same_declaration_twice(self):
        with self.assertRaisesRegex(ValueError, 'same declaration twice'):
            self.packet('package p\nfunc F() {}\n', ['F', 'p.F'])

    def test_oversized_unit_is_not_truncated(self):
        with self.assertRaisesRegex(ValueError, '6144 bytes'):
            self.packet('package p\nfunc F() {\n//' + 'x' * 6200 + '\n}\n')

    def test_duplicate_json_keys_refused(self):
        raw = b'{"source":"package bad","source":"package p\\nfunc F() {}\\n","path":"sample.go","selectors":["F"]}'
        with self.assertRaisesRegex(ValueError, 'duplicate field'):
            TOOL.run(raw)

    def test_invalid_surrogate_refused_but_literal_escape_text_preserved(self):
        raw = b'{"source":"package p\\n//\\ud800\\nfunc F() {}\\n","path":"sample.go","selectors":["F"]}'
        with self.assertRaisesRegex(ValueError, 'Unicode'):
            TOOL.run(raw)
        source = 'package p\nfunc F() string { return `\\ud800` }\n'
        self.assertIn('\\ud800', self.packet(source)['units'][0]['quote'])

    def test_return_tuple_metadata_preserves_expression_order_without_runtime_claim(self):
        unit = self.packet('package p\nfunc F() (int,error) { return value, err }\n')['units'][0]
        self.assertEqual('func() (int, error)', unit['function_type'])
        self.assertEqual(['value', 'err'], unit['return_contract']['expressions'])
        self.assertFalse(unit['return_contract']['runtime_completion_verified'])

    def test_callback_metadata_marks_unanalyzed_body_explicitly(self):
        unit = self.packet('package p\nfunc F() func() { return func() { lock(); mutate() } }\n')['units'][0]
        self.assertEqual('sole-return-function-literal', unit['return_contract']['kind'])
        self.assertFalse(unit['return_contract']['callback_body_analyzed'])
        self.assertNotIn('callback_contract', unit['return_contract'])

    def test_bare_return_and_additional_work_do_not_get_return_contract(self):
        for source in ['package p\nfunc F() (x int) { return }\n',
                       'package p\nfunc F() int { log(); return 7 }\n']:
            with self.subTest(source=source):
                self.assertNotIn('return_contract', self.packet(source)['units'][0])

    def test_generic_receiver_type_metadata_comes_from_ast(self):
        unit = self.packet('package p\nfunc (s *Store[T]) Get(x T) T { return x }\n', ['Store.Get'])['units'][0]
        self.assertEqual('*Store[T]', unit['receiver_type'])
        self.assertEqual('func(x T) T', unit['function_type'])
        self.assertEqual('p.Store.Get', unit['symbol'])

    def test_standalone_type_keeps_keyword_fields_and_physical_quote(self):
        source = 'package p\ntype Record struct {\n Value int\n}\n'
        unit = self.packet(source, ['p.Record'])['units'][0]
        self.assertEqual('type', unit['declaration_kind'])
        self.assertEqual('p.Record', unit['symbol'])
        self.assertEqual('\n'.join(source.split('\n')[1:4]), unit['quote'])
        self.assertEqual([2, 4], [unit['start_line'], unit['end_line']])
        self.assertNotIn('return_contract', unit)

    def test_alias_is_distinguished_from_defined_type(self):
        source = 'package p\ntype Alias = int\ntype Defined int\n'
        units = self.packet(source, ['Alias', 'Defined'])['units']
        self.assertEqual(['type-alias', 'type'], [unit['declaration_kind'] for unit in units])

    def test_generic_constraint_and_generic_alias_are_syntax_only(self):
        source = 'package p\ntype Ordered interface { ~int | ~float64 | ~string }\ntype Vector[T any] = []T\n'
        result = self.packet(source, ['Ordered', 'Vector'])
        self.assertEqual(['type', 'type-alias'], [unit['declaration_kind'] for unit in result['units']])
        self.assertTrue(result['syntax_only'])

    def test_grouped_type_is_refused_without_hiding_later_function(self):
        source = 'package p\ntype (A int; B string)\nfunc F() {}\n'
        with self.assertRaisesRegex(ValueError, '0 matches'):
            self.packet(source, ['A'])
        self.assertEqual('function', self.packet(source)['units'][0]['declaration_kind'])

    def test_type_alias_duplicates_and_same_line_adjacent_source_refuse(self):
        for source, selectors in [('package p\ntype A int\n', ['A', 'p.A']),
                                  ('package p\ntype A int; type B string\n', ['A'])]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                self.packet(source, selectors)

    def test_process_signal_is_reported_without_claiming_source_syntax_error(self):
        result = mock.Mock(returncode=-9, stderr=b'', stdout=b'')
        with mock.patch.object(TOOL.subprocess, 'run', return_value=result):
            with self.assertRaisesRegex(ValueError, 'terminated by signal 9'):
                TOOL.run(b'{}')

    def test_native_platform_lookup_refuses_windows_without_fallback(self):
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            TOOL.executable(system='Windows', machine='AMD64')

    def test_request_limit_refuses_before_binary_execution(self):
        with mock.patch.object(TOOL.subprocess, 'run') as execution:
            with self.assertRaisesRegex(ValueError, 'too large'):
                TOOL.run(b'x' * (TOOL.MAX_REQUEST + 1))
            execution.assert_not_called()

    def test_tampered_source_binary_and_symlink_fail_before_execution(self):
        native, _, _ = TOOL.executable()
        for mode in ['source', 'binary', 'symlink']:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory) / 'tool'
                shutil.copytree(TOOL.TOOL_ROOT, root)
                if mode == 'source':
                    (root / 'main.go').write_text('// altered')
                elif mode == 'binary':
                    (root / 'bin' / native.name).write_bytes(b'altered')
                else:
                    (root / 'bin' / native.name).unlink()
                    (root / 'bin' / native.name).symlink_to(native)
                with mock.patch.object(TOOL.subprocess, 'run') as execution:
                    with self.assertRaises(ValueError):
                        TOOL.run(b'{}', tool_root=root)
                    execution.assert_not_called()


if __name__ == '__main__':
    unittest.main()
