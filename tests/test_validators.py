from unittest import TestCase

import ciptools.validators
from ciptools.validators import ValidationError


class ValidationTests(TestCase):
    def test_time_range_validation(self):
        f = ciptools.validators.validate_time_range
        self.assertEqual(f("1m"), 60)
        self.assertEqual(f("1d"), 86400)
        self.assertEqual(f("1h"), 3600)
        self.assertEqual(f("1d1m"), 86400 + 60)
        self.assertEqual(f("1h1d1m"), 86400 + 3600 + 60)
        self.assertEqual(f("732"), 732)
        self.assertEqual(f("1h732"), 3600 + 732)

    def test_time_range_failures(self):
        f = ciptools.validators.validate_time_range
        self.assertRaises(ValidationError, f, "")
        self.assertRaises(ValidationError, f, "asdf")
        self.assertRaises(ValidationError, f, "1y")

    def test_percentage_validation(self):
        f = ciptools.validators.validate_percentage
        self.assertEqual(f("100%"), 100)
        self.assertEqual(f("50%"), 50)
        self.assertEqual(f("0%"), 0)

    def test_percentage_validation_failures(self):
        f = ciptools.validators.validate_percentage
        self.assertRaises(ValidationError, f, "")
        self.assertRaises(ValidationError, f, "101%")
        self.assertRaises(ValidationError, f, "-9%")
        self.assertRaises(ValidationError, f, "12")
        self.assertRaises(ValidationError, f, "asdf")

    def test_size_validation(self):
        f = ciptools.validators.validate_byte_size
        self.assertEqual(f("1"), 1)
        self.assertEqual(f("2K"), 2048)
        self.assertEqual(f("35M"), 36700160)
        self.assertEqual(f("1G"), 1073741824)
        self.assertEqual(f("1g"), 1073741824)

    def test_size_validation_failures(self):
        f = ciptools.validators.validate_byte_size
        self.assertRaises(ValidationError, f, "")
        self.assertRaises(ValidationError, f, "1Gi")
        self.assertRaises(ValidationError, f, "1Gb")
        self.assertRaises(ValidationError, f, "1Tb")
        self.assertRaises(ValidationError, f, "1G2K")
        self.assertRaises(ValidationError, f, "asdf")
