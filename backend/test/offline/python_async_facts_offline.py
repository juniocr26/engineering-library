import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    'python_async_facts', Path(__file__).resolve().parents[2] / 'lib/documentation/python_async_facts.py'
)
facts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(facts)


class AwaitedReturnShapeTest(unittest.TestCase):
    source = (
        'async def forward(callback, *values, **options):\n'
        '    callback = binder(callback, *values, **options)\n'
        '    return await runner(callback)\n'
    )

    def test_names_are_syntax_and_forwarded_argument_kinds_are_preserved(self):
        ir = facts.record(self.source, 'forward')
        self.assertEqual('local-call-awaited-return', ir['shape'])
        self.assertEqual('binder(callback, *values, **options)', ir['binding_call'])
        self.assertEqual('runner(callback)', ir['returned_call'])
        self.assertFalse(ir['source_executed'])
        self.assertIn('name bindings', facts.render(ir, 'en'))

    def test_docstring_and_crlf_preserve_exact_physical_quote(self):
        source = self.source.replace('    callback =', '    """Owned synthetic example."""\n    callback =')
        for text in (source, source.replace('\n', '\r\n')):
            ir = facts.record('marker = "a\u2028b"\n' + text, 'forward')
            self.assertEqual(2, ir['line'])
            self.assertEqual(5, ir['end_line'])
            self.assertEqual(text, ir['quote'])

    def test_methods_are_outside_forwarded_return_profile(self):
        source = 'class Container:\n' + ''.join('    ' + line for line in self.source.splitlines(True))
        with self.assertRaises(facts.Unsupported):
            facts.record(source, 'Container.forward')

    def test_extra_parameter_kinds_and_defaults_are_refused(self):
        for parameters in (
            'callback, /, *values, **options',
            'callback, extra, *values, **options',
            'callback, *values, enabled=True, **options',
            'callback=None, *values, **options',
            'callback, *values',
            'callback, **options',
        ):
            with self.subTest(parameters=parameters), self.assertRaises(facts.Unsupported):
                facts.record(self.source.replace('callback, *values, **options', parameters, 1), 'forward')

    def test_assignment_and_await_must_use_exact_selected_parameter(self):
        for text in (
            self.source.replace('callback =', 'alias ='),
            self.source.replace('callback =', 'alias = callback ='),
            self.source.replace('binder(callback,', 'binder(other,'),
            self.source.replace('binder(callback, *values, **options)', 'binder(callback, *options, **values)'),
            self.source.replace('runner(callback)', 'runner(other)'),
            self.source.replace('runner(callback)', 'runner(callback, extra=True)'),
            self.source.replace('binder(callback, *values, **options)', 'binder(callback, values, **options)'),
        ):
            with self.subTest(source=text), self.assertRaises(facts.Unsupported):
                facts.record(text, 'forward')

    def test_computed_and_subscripted_callees_are_refused(self):
        for expression in ('factory().runner', 'runners[0]', '(lambda x: x)'):
            with self.subTest(expression=expression), self.assertRaises(facts.Unsupported):
                facts.record(self.source.replace('runner(callback)', expression + '(callback)'), 'forward')

    def test_control_flow_and_result_discard_are_not_silently_rewritten(self):
        for text in (
            self.source.replace('return await', 'await'),
            self.source.replace('return await', 'return'),
            self.source.replace('return await runner(callback)', 'return None'),
            self.source + '    audit()\n',
            self.source.replace('    return await', '    if ready:\n        return await'),
        ):
            with self.subTest(source=text), self.assertRaises(facts.Unsupported):
                facts.record(text, 'forward')


class GuardedIterationShapeTest(unittest.TestCase):
    source = (
        'async def stream(values):\n'
        '    cursor = adapt(values)\n'
        '    while True:\n'
        '        try:\n'
        '            yield await backend.pull(advance, cursor)\n'
        '        except Finished:\n'
        '            break\n'
    )

    def test_ordered_calls_and_break_are_recorded_without_helper_claims(self):
        ir = facts.record(self.source, 'stream')
        self.assertEqual('local-call-guarded-yield-await', ir['shape'])
        self.assertEqual('adapt(values)', ir['initial_call'])
        self.assertEqual('backend.pull(advance, cursor)', ir['yielded_call'])
        self.assertEqual('Finished', ir['exception_name'])
        self.assertEqual(self.source, ir['quote'])
        en, pt = [facts.render(ir, lang) for lang in ('en', 'pt-br')]
        import re
        self.assertEqual(re.findall(r'`([^`]+)`', en), re.findall(r'`([^`]+)`', pt))
        self.assertIn('not returned as a final value', en)
        self.assertIn('exception matching', en)
        self.assertFalse(ir['source_executed'])

    def test_changed_names_are_recorded_without_builtin_or_import_resolution(self):
        text = self.source.replace('adapt', 'custom.convert').replace('Finished', 'Anything')
        ir = facts.record(text, 'stream')
        self.assertEqual('custom.convert(values)', ir['initial_call'])
        self.assertEqual('Anything', ir['exception_name'])

    def test_unicode_prior_literal_crlf_and_docstring_keep_physical_quote(self):
        text = self.source.replace('    cursor', '    """source note"""\n    cursor', 1)
        for quote in (text, text.replace('\n', '\r\n')):
            ir = facts.record('marker = "a\u2028b"\n' + quote, 'stream')
            self.assertEqual(2, ir['line'])
            self.assertEqual(9, ir['end_line'])
            self.assertEqual(quote, ir['quote'])

    def test_source_is_parsed_without_executing_top_level_code(self):
        ir = facts.record('raise RuntimeError("never execute inspected source")\n' + self.source, 'stream')
        self.assertEqual(2, ir['line'])

    def test_parameters_defaults_and_class_methods_are_outside_profile(self):
        for params in ('values, /', 'values=None', 'values, extra', '*values', 'values, *extra',
                       'values, **extra', 'values, *, enabled=True'):
            with self.subTest(params=params), self.assertRaises(facts.Unsupported):
                facts.record(self.source.replace('stream(values)', 'stream(' + params + ')'), 'stream')
        text = 'class Owner:\n' + ''.join('    ' + line for line in self.source.splitlines(True))
        with self.assertRaises(facts.Unsupported):
            facts.record(text, 'Owner.stream')

    def test_loop_condition_else_and_extra_work_are_not_dropped(self):
        for text in (
            self.source.replace('while True:', 'while 1:'),
            self.source.replace('while True:', 'while ready:'),
            self.source + '    else:\n        notify()\n',
            self.source + '    cleanup()\n',
            self.source.replace('        try:', '        audit()\n        try:'),
        ):
            with self.subTest(source=text), self.assertRaises(facts.Unsupported):
                facts.record(text, 'stream')

    def test_exception_handlers_else_and_finally_are_not_simplified(self):
        for text in (
            self.source.replace('except Finished:', 'except:'),
            self.source.replace('except Finished:', 'except (Finished, Other):'),
            self.source.replace('except Finished:', 'except errors.Finished:'),
            self.source.replace('except Finished:', 'except Finished as error:'),
            self.source.replace('            break', '            raise'),
            self.source.replace('            break', '            return'),
            self.source.replace('            break', '            log()\n            break'),
            self.source + '        except Other:\n            break\n',
            self.source + '        else:\n            audit()\n',
            self.source + '        finally:\n            cleanup()\n',
        ):
            with self.subTest(source=text), self.assertRaises(facts.Unsupported):
                facts.record(text, 'stream')

    def test_yield_await_and_exact_cursor_argument_are_required(self):
        for expr in ('await backend.pull(advance, cursor)', 'yield backend.pull(advance, cursor)',
                     'yield await backend.pull(advance, other)', 'yield await backend.pull(cursor)',
                     'yield await backend.pull(advance, cursor, extra)',
                     'yield await backend.pull(advance, cursor, flag=True)',
                     'yield await backend.pull(advance(), cursor)',
                     'yield await factory().pull(advance, cursor)',
                     'yield await backends[0](advance, cursor)'):
            text = self.source.replace('yield await backend.pull(advance, cursor)', expr)
            with self.subTest(expr=expr), self.assertRaises(facts.Unsupported):
                facts.record(text, 'stream')

    def test_initializer_argument_assignment_and_computed_target_are_refused(self):
        for expr in ('cursor = adapt(other)', 'cursor = adapt(values, extra)',
                     'cursor = adapt(values, option=True)', 'values = adapt(values)',
                     'cursor = other = adapt(values)', 'state.cursor = adapt(values)',
                     'cursor = factory().adapt(values)', 'cursor = adapters[0](values)'):
            with self.subTest(expr=expr), self.assertRaises(facts.Unsupported):
                facts.record(self.source.replace('cursor = adapt(values)', expr), 'stream')

    def test_extra_try_statement_and_decorators_are_refused(self):
        for text in (
            '@wrapper\n' + self.source,
            self.source.replace('            yield', '            audit()\n            yield'),
            self.source.replace('async def', 'def', 1),
        ):
            with self.subTest(source=text), self.assertRaises(facts.Unsupported):
                facts.record(text, 'stream')


if __name__ == '__main__':
    unittest.main()
