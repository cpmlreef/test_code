#main.py
from functions.import_git_repo import check_repo_accessibility
from functions.import_git_path_to_typedb import import_structure_to_typedb
from functions.import_file_list import import_files_to_typedb
from functions.file_audit import FileAuditor
import shutil
import os
import stat
import time
import signal
import openai

username = "cpachdach"
password = "hasd291ldasD"

def get_git_path_credentials():
    username = input("Enter your username: ")
    password = input("Enter your password: ")  
    return username, password

def get_git_path_from_user():
    return "https://github.com/bugen/pypipe"

def import_git_repo(git_repo_url):
    print(f"Checking accessibility of repository: {git_repo_url}")
    result = check_repo_accessibility(git_repo_url)

    if result["status"] == "auth_required":
        print("Authentication required. Please enter credentials.")
        username, password = get_git_path_credentials()
        result = check_repo_accessibility(git_repo_url, username, password)
    
    print(result["message"])
    
    if result["status"] == "success":
        print("Repository is accessible. Starting import process...")
        cache_dir = result.get("cache_dir")
        import_structure_to_typedb(git_repo_url, cache_dir)
        file_paths = FileAuditor.fetch_files_from_repo(git_repo_url)
        return cache_dir, file_paths
    return None, None

def on_rm_error(func, path, exc_info):
    # Remove read-only and system attributes.
    os.chmod(path, stat.S_IWRITE)
    try:
        if not os.path.isdir(path):
            os.system(f'attrib -H -S "{path}"')  # Remove hidden and system attributes.
            os.unlink(path)
        else:
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    os.chmod(file_path, stat.S_IWRITE)
                    os.system(f'attrib -H -S "{file_path}"')
                    os.unlink(file_path)
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(path)
    except Exception as e:
        print(f"Failed to delete {path}. Reason: {e}")

def force_remove_directory(dir_path, retries=3, delay=2):
    for attempt in range(retries):
        try:
            shutil.rmtree(dir_path, onerror=on_rm_error)
            print(f"Cleaned up the cache directory: {cache_dir}")
            break  # Exit the loop if deletion was successful
        except OSError as e:
            print(f"Error cleaning up the cache directory: {e}")
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)

def exit_gracefully(signum, frame):
    print("\nCTRL+C detected. Attempting to clean up and exit gracefully...")
    if cache_dir and os.path.exists(cache_dir):
        force_remove_directory(cache_dir)

# Register the exit_gracefully function to handle CTRL+C
signal.signal(signal.SIGINT, exit_gracefully)

if __name__ == '__main__':
    git_repo_url = get_git_path_from_user()
    cache_dir = None  # Initialize cache_dir to ensure it's available for cleanup

    try:
        print(f"Fetching file paths from repository: {git_repo_url}")
        cache_dir, file_paths = import_git_repo(git_repo_url)

        if cache_dir and file_paths:
            print("Starting AI auditing...")
            import_files_to_typedb(cache_dir, git_repo_url)
            audit_response = FileAuditor.ai_auditing(file_paths, cache_dir)
            print(f"Audit result for {file_paths[0]}: {audit_response}\n")
        else:
            print("No file paths found. AI auditing skipped.")
    except Exception as e:
        print(f"Error encountered: {e}")
    finally:
        if cache_dir:
            print(f"Attempting to clean up the cache directory: {cache_dir}")
            force_remove_directory(cache_dir)
