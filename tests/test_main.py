import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, call
import os
import tempfile
import shutil

# Assuming FileAuditor is in 'file_auditor.py' in the same directory or a discoverable path
# If it's in a package, adjust the import path accordingly.
# For example, if your project structure is:
# my_project/
#   auditing_module/
#     __init__.py
#     file_auditor.py
#     openai_auditor.py
#     audit_data_ingestion.py
#   tests/
#     test_file_auditor.py
#
# Then the import might be: from my_project.auditing_module.file_auditor import FileAuditor
# Or, if running tests from the `my_project` root: from auditing_module.file_auditor import FileAuditor

# For this example, let's assume file_auditor.py is in a module called 'auditor_module'
# and openai_auditor and audit_data_ingestion are also in it.
# To make this runnable, create a dummy structure:
# ./auditor_module/__init__.py (empty)
# ./auditor_module/file_auditor.py (your script)
# ./auditor_module/openai_auditor.py (dummy for testing)
# ./auditor_module/audit_data_ingestion.py (dummy for testing)

# Dummy openai_auditor.py for testing context
# class OpenAI_Auditor:
#     def __init__(self):
#         print("Mock OpenAI_Auditor initialized")
#     def audit_content(self, content):
#         print(f"Mock OpenAI_Auditor auditing content: {content[:30]}...")
#         return {"mock_response": "audited", "content_preview": content[:10]}

# Dummy audit_data_ingestion.py for testing context
# def ingest_audit_data_to_typedb(response, file_path):
#     print(f"Mock ingest_audit_data_to_typedb for {file_path} with response: {response}")
#     return True

# If the above dummies are not created as files, mocks will handle them.
# The patch paths below assume 'file_auditor' is the module where FileAuditor is defined,
# and it imports '.openai_auditor' and '.audit_data_ingestion'.
# So the patch target will be 'your_module_name.file_auditor.OpenAI_Auditor' etc.
# Let's assume the file_auditor.py is in a module named 'source_module'
# and the test is in 'tests/' directory.
# The imports in file_auditor.py are relative: from .openai_auditor import OpenAI_Auditor
# This means when file_auditor is imported, it looks for openai_auditor in the same package.

# For simplicity of running this standalone, I'll assume file_auditor.py is the direct target.
# If your actual structure is `project.module.file_auditor`, adjust patch paths.
# Let's assume the file with FileAuditor is `file_auditor_script.py`
# and the imports are `from .openai_auditor import OpenAI_Auditor`
# we would patch `file_auditor_script.OpenAI_Auditor` and `file_auditor_script.audit_data_ingestion`

# To make it runnable without complex setup, let's assume file_auditor.py is the main script
# and the other modules are also in the same directory for this test setup.
# If `file_auditor.py` is in `src/auditing/file_auditor.py`, then patch targets would be
# `src.auditing.file_auditor.TypeDB`, `src.auditing.file_auditor.OpenAI_Auditor` etc.

# Let's make an assumption for the patch path. If `FileAuditor` is in `main_auditor_script.py`:
# MAIN_AUDITOR_SCRIPT_PATH = "main_auditor_script" # if file is main_auditor_script.py
# If FileAuditor is in project/module/file_auditor.py, then:
# MAIN_AUDITOR_SCRIPT_PATH = "project.module.file_auditor"

# For this self-contained example, let's assume the FileAuditor code is in `file_auditor_module.py`
# and test script is alongside it.
# Create `file_auditor_module.py` with your FileAuditor class.
# Create `openai_auditor.py` and `audit_data_ingestion.py` in the same directory as dummy modules.
# openai_auditor.py:
# class OpenAI_Auditor:
#     def audit_content(self, content): return {"issues": []}
#
# audit_data_ingestion.py:
# def ingest_audit_data_to_typedb(response, file_path): pass

# The import for FileAuditor itself needs to be correct.
# If `file_auditor.py` is where the class is, and test is in same dir:
from file_auditor import FileAuditor # This assumes your script is named file_auditor.py
# And the patch targets will be relative to 'file_auditor' module

# Patch targets reflect where the names are *looked up*, not where they are defined.
# Since file_auditor.py does `from typedb.driver import TypeDB`, we patch `file_auditor.TypeDB`
# Since file_auditor.py does `from .openai_auditor import OpenAI_Auditor`, we patch `file_auditor.OpenAI_Auditor`
# Since file_auditor.py does `from . import audit_data_ingestion`, we patch `file_auditor.audit_data_ingestion`

@patch('file_auditor.TypeDB') # Patch where TypeDB is used in file_auditor.py
@patch('file_auditor.OpenAI_Auditor') # Patch where OpenAI_Auditor is used
@patch('file_auditor.audit_data_ingestion') # Patch where audit_data_ingestion is used
class TestFileAuditor(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for cache
        self.temp_cache_dir = tempfile.mkdtemp()
        # Create some dummy files in the cache
        self.file1_name = "script.py"
        self.file2_name = "another.java"
        self.file3_name = "readme.md" # Non-code file
        self.file1_path_in_repo = f"/repo/src/{self.file1_name}"
        self.file2_path_in_repo = f"/repo/lib/{self.file2_name}"
        self.file3_path_in_repo = f"/repo/{self.file3_name}"

        with open(os.path.join(self.temp_cache_dir, self.file1_name), 'w') as f:
            f.write("python code here")
        with open(os.path.join(self.temp_cache_dir, self.file2_name), 'w') as f:
            f.write("java code here")
        with open(os.path.join(self.temp_cache_dir, self.file3_name), 'w') as f:
            f.write("this is a readme")

    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.temp_cache_dir)

    def test_fetch_files_from_repo_success(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_fetch_files_from_repo_success")
        mock_driver_instance = MockTypeDB.core_driver.return_value
        mock_session = mock_driver_instance.session.return_value.__enter__.return_value
        mock_tx = mock_session.transaction.return_value.__enter__.return_value

        # Simulate TypeDB query response
        mock_concept_map1 = MagicMock()
        mock_concept_map1.get.return_value.as_string.return_value = self.file1_path_in_repo
        mock_concept_map2 = MagicMock()
        mock_concept_map2.get.return_value.as_string.return_value = self.file2_path_in_repo
        
        mock_tx.query.match.return_value = [mock_concept_map1, mock_concept_map2]

        git_repo_url = "git@example.com:user/repo.git"
        audit_uuid = "test-uuid-123"
        
        file_paths = FileAuditor.fetch_files_from_repo(git_repo_url, audit_uuid)

        MockTypeDB.core_driver.assert_called_once_with(MockTypeDB.DEFAULT_ADDRESS)
        mock_driver_instance.session.assert_called_once_with("CodeDD_test_2", mock.ANY) # ANY for SessionType
        mock_session.transaction.assert_called_once_with(mock.ANY) # ANY for TransactionType
        
        expected_query_fragment_audit = f'has audit_uuid "{audit_uuid}"'
        expected_query_fragment_repo = f'has url "{git_repo_url}"'
        
        # Check if the query was called and contained key parts
        self.assertTrue(mock_tx.query.match.called)
        actual_query = mock_tx.query.match.call_args[0][0]
        self.assertIn(expected_query_fragment_audit, actual_query)
        self.assertIn(expected_query_fragment_repo, actual_query)

        self.assertEqual(len(file_paths), 2)
        self.assertIn(self.file1_path_in_repo, file_paths)
        self.assertIn(self.file2_path_in_repo, file_paths)
        mock_concept_map1.get.assert_called_with("path")
        mock_concept_map2.get.assert_called_with("path")

    def test_fetch_files_from_repo_no_files(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_fetch_files_from_repo_no_files")
        mock_driver_instance = MockTypeDB.core_driver.return_value
        mock_session = mock_driver_instance.session.return_value.__enter__.return_value
        mock_tx = mock_session.transaction.return_value.__enter__.return_value
        mock_tx.query.match.return_value = [] # No files found

        git_repo_url = "git@example.com:user/repo.git"
        audit_uuid = "test-uuid-empty"
        
        file_paths = FileAuditor.fetch_files_from_repo(git_repo_url, audit_uuid)
        self.assertEqual(len(file_paths), 0)

    def test_read_file_content_from_cache_found(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_read_file_content_from_cache_found")
        content = FileAuditor.read_file_content_from_cache(self.temp_cache_dir, self.file1_path_in_repo)
        self.assertEqual(content, "python code here")

        content_readme = FileAuditor.read_file_content_from_cache(self.temp_cache_dir, self.file3_path_in_repo)
        self.assertEqual(content_readme, "this is a readme")

    def test_read_file_content_from_cache_not_found(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_read_file_content_from_cache_not_found")
        with self.assertRaises(FileNotFoundError):
            FileAuditor.read_file_content_from_cache(self.temp_cache_dir, "/repo/non_existent_file.py")

    def test_filter_code_files(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_filter_code_files")
        file_paths = [
            "src/main.py",
            "docs/README.md",
            "LICENSE",
            "data/input.csv",
            "src/utils.js",
            "image.jpg",
            "archive.zip",
            "backup.bak",
            "script.sh", # Should typically be included as code
            "Makefile",  # Should typically be included
            "Dockerfile" # Should typically be included
        ]
        filtered_files = FileAuditor.filter_code_files(file_paths)
        expected_files = [
            "src/main.py",
            "src/utils.js",
            "script.sh",
            "Makefile",
            "Dockerfile"
        ]
        self.assertListEqual(sorted(filtered_files), sorted(expected_files))

    def test_filter_code_files_empty_input(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_filter_code_files_empty_input")
        self.assertEqual(FileAuditor.filter_code_files([]), [])

    def test_filter_code_files_no_code_files(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_filter_code_files_no_code_files")
        file_paths = ["README.md", "data.json", "LICENSE.txt"]
        self.assertEqual(FileAuditor.filter_code_files(file_paths), [])

    def test_ai_auditing_success(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_ai_auditing_success")
        # Setup mock for OpenAI_Auditor instance
        mock_auditor_instance = MockOpenAI_Auditor.return_value
        mock_auditor_instance.audit_content.return_value = {"issues": [], "report": "all good"}

        # Mock the static methods of FileAuditor that are called internally, or let them run
        # For this test, we'll let filter_code_files and read_file_content_from_cache run.
        
        repo_file_paths = [self.file1_path_in_repo, self.file2_path_in_repo, self.file3_path_in_repo]
        
        success = FileAuditor.ai_auditing(repo_file_paths, self.temp_cache_dir)

        self.assertTrue(success)
        MockOpenAI_Auditor.assert_called_once() # Check if constructor was called
        
        # Check calls to audit_content
        # self.file3_path_in_repo (readme.md) should be filtered out
        expected_audit_content_calls = [
            call("python code here"),
            call("java code here")
        ]
        mock_auditor_instance.audit_content.assert_has_calls(expected_audit_content_calls, any_order=True)
        self.assertEqual(mock_auditor_instance.audit_content.call_count, 2)

        # Check calls to ingest_audit_data_to_typedb
        expected_ingestion_calls = [
            call({"issues": [], "report": "all good"}, self.file1_path_in_repo),
            call({"issues": [], "report": "all good"}, self.file2_path_in_repo)
        ]
        mock_audit_ingestion.ingest_audit_data_to_typedb.assert_has_calls(expected_ingestion_calls, any_order=True)
        self.assertEqual(mock_audit_ingestion.ingest_audit_data_to_typedb.call_count, 2)

    def test_ai_auditing_no_code_files_to_audit(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_ai_auditing_no_code_files_to_audit")
        # Setup mock for OpenAI_Auditor instance
        mock_auditor_instance = MockOpenAI_Auditor.return_value
        
        repo_file_paths = [self.file3_path_in_repo] # Only readme.md
        
        success = FileAuditor.ai_auditing(repo_file_paths, self.temp_cache_dir)

        self.assertFalse(success) # As per current implementation "No code files to audit." returns False
        MockOpenAI_Auditor.assert_called_once() # Constructor still called
        mock_auditor_instance.audit_content.assert_not_called()
        mock_audit_ingestion.ingest_audit_data_to_typedb.assert_not_called()

    def test_ai_auditing_file_not_found_in_cache(self, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_ai_auditing_file_not_found_in_cache")
        mock_auditor_instance = MockOpenAI_Auditor.return_value
        mock_auditor_instance.audit_content.return_value = {"issues": [], "report": "all good"}

        # One file exists, one does not
        non_existent_file_path = "/repo/src/non_existent.py"
        repo_file_paths = [self.file1_path_in_repo, non_existent_file_path]
        
        success = FileAuditor.ai_auditing(repo_file_paths, self.temp_cache_dir)

        self.assertFalse(success)
        MockOpenAI_Auditor.assert_called_once()
        
        # file1.py should be audited
        mock_auditor_instance.audit_content.assert_called_once_with("python code here")
        mock_audit_ingestion.ingest_audit_data_to_typedb.assert_called_once_with(
            {"issues": [], "report": "all good"}, self.file1_path_in_repo
        )
        
        # non_existent.py should cause a FileNotFoundError, which is caught and logged.
        # No further calls for non_existent.py to audit_content or ingest_audit_data

    @patch('file_auditor.FileAuditor.read_file_content_from_cache') # Mock a specific method of FileAuditor
    def test_ai_auditing_internal_read_error(self, mock_read_content, mock_audit_ingestion, MockOpenAI_Auditor, MockTypeDB):
        print("\nRunning test_ai_auditing_internal_read_error")
        # Setup mock for OpenAI_Auditor instance
        mock_auditor_instance = MockOpenAI_Auditor.return_value

        # Simulate read_file_content_from_cache raising FileNotFoundError for the second file
        # This is an alternative way to test FileNotFoundError handling within ai_auditing
        mock_read_content.side_effect = [
            "python code here", # For self.file1_path_in_repo
            FileNotFoundError("Cache miss for test")
        ]
        
        repo_file_paths = [self.file1_path_in_repo, self.file2_path_in_repo] # file2 will cause error via mock
        
        success = FileAuditor.ai_auditing(repo_file_paths, self.temp_cache_dir)

        self.assertFalse(success)
        MockOpenAI_Auditor.assert_called_once()
        
        # file1.py should be audited
        mock_auditor_instance.audit_content.assert_called_once_with("python code here")
        mock_audit_ingestion.ingest_audit_data_to_typedb.assert_called_once_with(
            mock.ANY, self.file1_path_in_repo
        )
        
        # Check calls to read_file_content_from_cache
        expected_read_calls = [
            call(self.temp_cache_dir, self.file1_path_in_repo),
            call(self.temp_cache_dir, self.file2_path_in_repo) # This one raises error
        ]
        mock_read_content.assert_has_calls(expected_read_calls)
        self.assertEqual(mock_read_content.call_count, 2)


if __name__ == '__main__':
    # To make this runnable, you'd need:
    # 1. Your `FileAuditor` class in a file named `file_auditor.py` in the same directory.
    # 2. Dummy `openai_auditor.py` and `audit_data_ingestion.py` in the same directory:
    #    `openai_auditor.py`:
    #    ```python
    #    class OpenAI_Auditor:
    #        def __init__(self, api_key=None): # Match constructor if it takes args
    #            pass
    #        def audit_content(self, content):
    #            return {"mock_openai_response": "audited"}
    #    ```
    #    `audit_data_ingestion.py`:
    #    ```python
    #    def ingest_audit_data_to_typedb(response, file_path):
    #        pass # Mock implementation
    #    ```
    # 3. `typedb-driver` installed (though it's mocked, TypeDB class needs to be importable)
    
    # Create dummy files for imports to work if they don't exist
    # This is a bit hacky for a self-contained example. 
    # In a real project, your structure would handle this.
    
    if not os.path.exists("openai_auditor.py"):
        with open("openai_auditor.py", "w") as f:
            f.write("class OpenAI_Auditor:\n")
            f.write("    def __init__(self, api_key=None):\n") # Adjusted for potential api_key arg
            f.write("        print('Mock OpenAI_Auditor initialized in dummy file')\n")
            f.write("    def audit_content(self, content):\n")
            f.write("        return {'issues': [], 'report': 'mock audit success'}\n")

    if not os.path.exists("audit_data_ingestion.py"):
        with open("audit_data_ingestion.py", "w") as f:
            f.write("def ingest_audit_data_to_typedb(response, file_path):\n")
            f.write("    print(f'Mock ingest_audit_data_to_typedb called for {file_path} in dummy file')\n")
            f.write("    return True\n")
            
    # Ensure __init__.py exists if file_auditor.py uses relative imports like from .openai_auditor
    # If file_auditor.py is in the root and uses from openai_auditor (no dot), this isn't needed.
    # Given the `from .` imports, it implies a package. Let's assume the test and modules are
    # flat for this example, and adjust file_auditor.py's imports or patch targets.
    # For `from .openai_auditor`, it means `file_auditor.py` must be part of a package.
    # To simplify:
    # 1. Put `file_auditor.py`, `openai_auditor.py`, `audit_data_ingestion.py`, `test_file_auditor.py`
    #    all in a directory, say `my_auditing_pkg`.
    # 2. Add an empty `__init__.py` to `my_auditing_pkg`.
    # 3. In `file_auditor.py`, keep `from .openai_auditor import OpenAI_Auditor` and `from . import audit_data_ingestion`.
    # 4. In `test_file_auditor.py`, change `from file_auditor import FileAuditor` to `from .file_auditor import FileAuditor`.
    # 5. Run `python -m unittest test_file_auditor.py` from *outside* `my_auditing_pkg`.
    #
    # OR, if `file_auditor.py`'s imports were `from openai_auditor import ...` (absolute/sibling),
    # and all files are in the same dir, then `python test_file_auditor.py` might work directly.
    # The current `from .module` implies `file_auditor.py` is part of a package.
    # The patches `file_auditor.TypeDB` etc. assume `file_auditor` is the module name.

    unittest.main(argv=['first-arg-is-ignored'], exit=False, verbosity=2)

    # Clean up dummy files
    # if os.path.exists("openai_auditor.pyc"): os.remove("openai_auditor.pyc")
    # if os.path.exists("__pycache__"): shutil.rmtree("__pycache__")
    # if os.path.exists("openai_auditor.py") and "Mock OpenAI_Auditor initialized" in open("openai_auditor.py").read():
    #     os.remove("openai_auditor.py")
    # if os.path.exists("audit_data_ingestion.py") and "Mock ingest_audit_data_to_typedb called" in open("audit_data_ingestion.py").read():
    #     os.remove("audit_data_ingestion.py")
