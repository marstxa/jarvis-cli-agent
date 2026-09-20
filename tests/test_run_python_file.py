import subprocess
import unittest
from unittest.mock import patch

from jarvis.tools.run_python_file import run_python_file


class TestRunPythonFile(unittest.TestCase):
    def test_runs_with_no_args(self):
        result = run_python_file("calculator", "main.py")
        self.assertIn("Calculator App", result)

    def test_runs_with_args(self):
        result = run_python_file("calculator", "main.py", ["3 + 5"])
        self.assertIn('"result": 8', result)

    def test_runs_test_suite(self):
        result = run_python_file("calculator", "tests.py")
        self.assertIn("OK", result)

    def test_rejects_path_outside_sandbox(self):
        result = run_python_file("calculator", "../main.py")
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("outside the permitted working directory", result)

    def test_rejects_nonexistent_file(self):
        result = run_python_file("calculator", "nonexistent.py")
        self.assertTrue(result.startswith("Error:"))

    def test_rejects_non_python_file(self):
        result = run_python_file("calculator", "lorem.txt")
        self.assertTrue(result.startswith("Error:"))
        self.assertIn("not a Python file", result)

    def test_nonzero_exit_still_surfaces_stdout_and_stderr(self):
        # Regression test: a non-zero exit code used to discard stdout and
        # stderr entirely, returning only "Process exited with code 1" with
        # no clue what actually failed. Mock subprocess.run so this is
        # verified directly rather than depending on a script that happens
        # to exit non-zero.
        fake_result = subprocess.CompletedProcess(
            args=["python", "main.py"],
            returncode=1,
            stdout="partial output before the crash\n",
            stderr="Traceback (most recent call last):\nValueError: boom\n",
        )
        with patch("jarvis.tools.run_python_file.subprocess.run", return_value=fake_result):
            result = run_python_file("calculator", "main.py")

        self.assertIn("partial output before the crash", result)
        self.assertIn("ValueError: boom", result)
        self.assertIn("Process exited with code 1", result)


if __name__ == "__main__":
    unittest.main()
