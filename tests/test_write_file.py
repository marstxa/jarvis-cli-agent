import os
import unittest

from jarvis.tools.write_file import write_file


class TestWriteFile(unittest.TestCase):
    def setUp(self):
        # Write to a dedicated scratch file rather than the demo fixtures
        # (lorem.txt, pkg/morelorem.txt), so running the tests doesn't
        # overwrite files the calculator/ sandbox ships with.
        self.scratch_path = os.path.join(os.path.abspath("calculator"), "_test_scratch.txt")

    def tearDown(self):
        if os.path.exists(self.scratch_path):
            os.remove(self.scratch_path)

    def test_writes_new_file(self):
        content = "hello from the test suite"
        result = write_file("calculator", "_test_scratch.txt", content)
        self.assertIn("Successfully wrote", result)
        with open(self.scratch_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

    def test_creates_missing_parent_directories(self):
        result = write_file("calculator", "_scratch_dir/nested.txt", "nested content")
        nested_path = os.path.join(os.path.abspath("calculator"), "_scratch_dir", "nested.txt")
        try:
            self.assertIn("Successfully wrote", result)
            self.assertTrue(os.path.exists(nested_path))
        finally:
            if os.path.exists(nested_path):
                os.remove(nested_path)
                os.rmdir(os.path.dirname(nested_path))

    def test_rejects_path_outside_sandbox(self):
        result = write_file("calculator", "/tmp/should_not_be_allowed.txt", "nope")
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("outside the permitted working directory", result)

    def test_rejects_writing_over_a_directory(self):
        result = write_file("calculator", "pkg", "nope")
        self.assertTrue(result.startswith("Error:"))


if __name__ == "__main__":
    unittest.main()
