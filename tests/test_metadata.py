from unittest import TestCase

import pytest

import ciptools.metadata


class ConversionTests(TestCase):
    def test_version(self):
        f = ciptools.metadata.version
        self.assertEqual(f("ciptools"), "0.0.0")
        self.assertEqual(f("pytest"), pytest.__version__)
