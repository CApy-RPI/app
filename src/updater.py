import os
import time
import subprocess
from dotenv import load_dotenv
from functools import wraps

# Load environment variables from .env file
load_dotenv()

# Get the repository directory from the environment variable
REPO_DIR = os.getenv("REPO_DIR")

if not REPO_DIR:
    raise ValueError("REPO_DIR not set in .env file.")

# Constants
MAX_RETRIES = 5
RETRY_DELAY = 300  # 5 minutes in seconds


def retry_on_failure(max_retries=MAX_RETRIES):
    """Decorator to retry a function on failure."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for retries in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except subprocess.CalledProcessError as e:
                    print(
                        f"Attempt {retries + 1}: An error occurred while executing {func.__name__}: {e}"
                    )
                    time.sleep(RETRY_DELAY)  # Wait before retrying
            print(f"Reached maximum retries for {func.__name__}.")
            return None  # Indicate failure

        return wrapper

    return decorator


@retry_on_failure()
def fetch_updates():
    """Fetch updates from the remote repository."""
    subprocess.run(["git", "fetch", "origin"], check=True)


@retry_on_failure()
def check_commits():
    """Check the current local and remote commits."""
    local_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    )
    remote_commit = subprocess.run(
        ["git", "rev-parse", "@{u}"], check=True, capture_output=True, text=True
    )
    return local_commit.stdout.strip(), remote_commit.stdout.strip()


@retry_on_failure()
def pull_changes():
    """Pull changes from the remote repository."""
    subprocess.run(["git", "pull", "origin", "main"], check=True)


@retry_on_failure()
def run_main_script():
    """Run the main.py script."""
    subprocess.run(["python3", "main.py"], check=True)


def main():
    """Main execution loop to check for updates and run the script."""
    while True:
        try:
            os.chdir(REPO_DIR)  # Change to the repository directory

            # Fetch the latest changes
            fetch_updates()

            # Check commits
            commits = check_commits()
            if commits is None:
                break  # Exit on failure after retries

            local_commit, remote_commit = commits

            # Compare local and remote commits
            if local_commit == remote_commit:
                print("No changes detected.")
                time.sleep(RETRY_DELAY)  # Wait before checking again
                continue  # Skip to the next iteration

            print("Changes detected. Pulling new changes...")
            if pull_changes() is None:
                break  # Exit on failure after retries

            # Run the main.py script
            print("Running the new main.py...")
            if run_main_script() is None:
                break  # Exit on failure after retries

        except Exception as e:
            print(f"An unexpected error occurred in the main loop: {e}")
            time.sleep(RETRY_DELAY)  # Wait before trying again


if __name__ == "__main__":
    main()
