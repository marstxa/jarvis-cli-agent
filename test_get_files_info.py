import unittest

from functions.get_files_info import get_files_info


class TestGetFilesInfo(unittest.TestCase):
    def test_lists_current_directory(self):
        result = get_files_info("calculator", ".")
        self.assertIn("main.py", result)
        self.assertIn("pkg", result)

    def test_lists_subdirectory(self):
        result = get_files_info("calculator", "pkg")
        self.assertIn("calculator.py", result)
        self.assertIn("render.py", result)

    def test_rejects_absolute_path_outside_sandbox(self):
        result = get_files_info("calculator", "/bin")
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("outside the permitted working directory", result)

    def test_rejects_parent_traversal(self):
        result = get_files_info("calculator", "../")
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("outside the permitted working directory", result)

    def test_rejects_nonexistent_directory(self):
        result = get_files_info("calculator", "does_not_exist")
        self.assertTrue(result.startswith("Error:"))

    def test_rejects_file_as_directory(self):
        result = get_files_info("calculator", "main.py")
        self.assertTrue(result.startswith("Error:"))


if __name__ == "__main__":
    unittest.main()
