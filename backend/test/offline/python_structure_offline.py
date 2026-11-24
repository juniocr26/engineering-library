import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('python_structure', Path(__file__).resolve().parents[2] / 'lib/documentation/python_structure.py')
structure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(structure)


class PythonPhysicalSourceLinesTest(unittest.TestCase):
    def test_unicode_separator_inside_literal_does_not_add_a_physical_line(self):
        for separator in ['\u2028', '\u2029', '\x85', '\v', '\f']:
            source = 'marker = "x' + separator + 'y"\ndef f():\n return 1\n'
            with self.subTest(separator=hex(ord(separator))):
                span = structure.ranges(source)[0]
                self.assertEqual((1, 3), (span['start'], span['end']))

    def test_crlf_and_lf_have_same_physical_span(self):
        source = 'def f():\n return 1\n'
        self.assertEqual(structure.ranges(source), structure.ranges(source.replace('\n', '\r\n')))

    def test_bare_cr_is_outside_explicit_physical_line_profile(self):
        with self.assertRaisesRegex(ValueError, 'bare CR'):
            structure.ranges('def f():\r return 1\r')


if __name__ == '__main__':
    unittest.main()
