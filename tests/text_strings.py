from unittest import TestCase

import ciptools.strings


class StringsTests(TestCase):
    def test_html_extraction(self):
        self.assertEqual(
            "this is text",
            ciptools.strings.extract_text_from_html("   <p>this</p> is text   "),
        )

        self.assertEqual(
            "this is text",
            ciptools.strings.extract_text_from_html("   <p>this is text   "),
        )

        self.assertEqual(
            "this is text",
            ciptools.strings.extract_text_from_html("  this</p> is text   "),
        )

        self.assertEqual(
            "this is text",
            ciptools.strings.extract_text_from_html("  this     </p> is text   "),
        )
