import unittest

from functions.get_file_content import get_file_content


class TestGetFileContent(unittest.TestCase):
    def test_reads_root_file(self):
        result = get_file_content("calculator", "main.py")
        self.assertIn("Calculator App", result)

    def test_reads_nested_file(self):
        result = get_file_content("calculator", "pkg/calculator.py")
        self.assertIn("class Calculator", result)

    def test_rejects_path_outside_sandbox(self):
        result = get_file_content("calculator", "../main.py")
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("outside the permitted working directory", result)

    def test_missing_file_returns_error_not_exception(self):
        result = get_file_content("calculator", "pkg/does_not_exist.py")
        self.assertTrue(result.startswith("Error:"))

    def test_directory_is_not_a_valid_file(self):
        result = get_file_content("calculator", "pkg")
        self.assertTrue(result.startswith("Error:"))


if __name__ == "__main__":
    unittest.main()
