from unittest import TestCase

import ciptools.converters


class ConversionTests(TestCase):
    def test_convert_time(self):
        f = ciptools.converters.convert_human_seconds
        self.assertEqual(f(None), "unknown")
        self.assertEqual(f("asdf"), "unknown")
        self.assertEqual(f("10"), "a few seconds")
        self.assertEqual(f(10), "a few seconds")
        self.assertEqual(f(60), "a minute")
        self.assertEqual(f(89), "a minute")
        self.assertEqual(f(90), "2 minutes")
        self.assertEqual(f(2000), "34 minutes")
        self.assertEqual(f(5000), "an hour")
        self.assertEqual(f(6400), "2 hours")
        self.assertEqual(f(86400), "a day")
        self.assertEqual(f(86400 * 10), "10 days")
        self.assertEqual(f(86400 * 30), "a month")
        self.assertEqual(f(86400 * 300), "10 months")
        self.assertEqual(f(86400 * 500), "a year")
        self.assertEqual(f(86400 * 600), "2 years")

    def test_convert_bytes(self):
        f = ciptools.converters.convert_human_bytes
        self.assertEqual(f(None), "unknown")
        self.assertEqual(f("asdf"), "unknown")
        self.assertEqual(f("1"), "1.0")
        self.assertEqual(f(1), "1.0")
        self.assertEqual(f(1000), "1000.0")
        self.assertEqual(f(2000), "2.0K")
        self.assertEqual(f(10000), "9.8K")
        self.assertEqual(f(10000000), "9.5M")
